"""
preprocess.py

Customer Churn SageMaker Pipeline

This script is executed by the SageMaker ProcessingStep.

Responsibilities
----------------
1. Read raw customer dataset
2. Clean missing values
3. Engineer date features
4. One-hot encode categorical variables
5. Split dataset into train / validation / test
6. Save CSV files for downstream XGBoost training
"""

import os
import argparse

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split


# ---------------------------------------------------------------------
# Feature Engineering
# ---------------------------------------------------------------------

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess the raw customer dataframe.
    """

    # ---------------------------------------------------------
    # Convert date columns
    # ---------------------------------------------------------

    date_columns = [
        "created",
        "firstorder",
        "lastorder",
    ]

    for col in date_columns:
        df[col] = pd.to_datetime(
            df[col],
            errors="coerce",
        )

    # ---------------------------------------------------------
    # Remove rows with missing values
    # ---------------------------------------------------------

    df = df.dropna()

    # ---------------------------------------------------------
    # Feature Engineering
    # ---------------------------------------------------------

    df["first_last_days_diff"] = (
        df["lastorder"] - df["firstorder"]
    ).dt.days

    df["created_first_days_diff"] = (
        df["created"] - df["firstorder"]
    ).dt.days

    # ---------------------------------------------------------
    # Remove unused columns
    # ---------------------------------------------------------

    drop_columns = [
        "custid",
        "created",
        "firstorder",
        "lastorder",
    ]

    df = df.drop(
        columns=drop_columns,
        errors="ignore",
    )

    # ---------------------------------------------------------
    # One-hot encoding
    # ---------------------------------------------------------

    categorical_columns = [
        "favday",
        "city",
    ]

    df = pd.get_dummies(
        df,
        columns=categorical_columns,
        prefix=categorical_columns,
    )

    return df


# ---------------------------------------------------------------------
# Dataset Split
# ---------------------------------------------------------------------

def split_dataset(df):

    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["retained"],
    )

    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["retained"],
    )

    return (
        train_df,
        validation_df,
        test_df,
    )


# ---------------------------------------------------------------------
# XGBoost Format
# Label column first
# ---------------------------------------------------------------------

def prepare_for_xgboost(df):

    label = df.pop("retained")

    df.insert(
        0,
        "retained",
        label,
    )

    return df


# ---------------------------------------------------------------------
# Save Outputs
# ---------------------------------------------------------------------

def save_dataframe(df, output_path):

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True,
    )

    df.to_csv(
        output_path,
        header=False,
        index=False,
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input-data",
        type=str,
        default="/opt/ml/processing/input/storedata_total.csv",
    )

    parser.add_argument(
        "--train-output",
        type=str,
        default="/opt/ml/processing/train/train.csv",
    )

    parser.add_argument(
        "--validation-output",
        type=str,
        default="/opt/ml/processing/validation/validation.csv",
    )

    parser.add_argument(
        "--test-output",
        type=str,
        default="/opt/ml/processing/test/test.csv",
    )

    args = parser.parse_args()

    print("Reading dataset...")

    df = pd.read_csv(args.input_data)

    print(f"Input rows : {len(df)}")
    print(f"Input cols : {len(df.columns)}")

    # ---------------------------------------------------------
    # Feature Engineering
    # ---------------------------------------------------------

    df = preprocess_dataframe(df)

    print(f"Processed rows : {len(df)}")
    print(f"Processed cols : {len(df.columns)}")

    # ---------------------------------------------------------
    # Split
    # ---------------------------------------------------------

    train_df, validation_df, test_df = split_dataset(df)

    print("Train :", train_df.shape)
    print("Validation :", validation_df.shape)
    print("Test :", test_df.shape)

    # ---------------------------------------------------------
    # XGBoost formatting
    # ---------------------------------------------------------

    train_df = prepare_for_xgboost(train_df)

    validation_df = prepare_for_xgboost(validation_df)

    test_df = prepare_for_xgboost(test_df)

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    save_dataframe(
        train_df,
        args.train_output,
    )

    save_dataframe(
        validation_df,
        args.validation_output,
    )

    save_dataframe(
        test_df,
        args.test_output,
    )

    print("Finished preprocessing.")


if __name__ == "__main__":
    main()