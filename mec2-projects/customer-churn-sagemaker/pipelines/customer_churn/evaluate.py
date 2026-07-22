"""
evaluate.py

Customer Churn SageMaker Pipeline

This script is executed as a SageMaker Processing Step after
HyperParameterTuning.

Responsibilities
----------------
1. Load the best XGBoost model.
2. Load the test dataset.
3. Generate predictions.
4. Calculate evaluation metrics.
5. Save evaluation.json for ConditionStep.
"""

import argparse
import json
import os
import pickle

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def load_model(model_path):
    """
    Load a trained XGBoost model.
    """

    print(f"Loading model from: {model_path}")

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    return model


def load_test_data(test_path):
    """
    Load test CSV produced by preprocess.py.

    The first column is the label.
    """

    print(f"Loading test dataset from: {test_path}")

    df = pd.read_csv(
        test_path,
        header=None,
    )

    y = df.iloc[:, 0]

    X = df.iloc[:, 1:]

    return X, y


def evaluate(model, X_test, y_test):
    """
    Calculate evaluation metrics.
    """

    # -----------------------------------------------------
    # Probabilities
    # -----------------------------------------------------

    probabilities = model.predict_proba(X_test)[:, 1]

    predictions = (probabilities >= 0.5).astype(int)

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    auc = roc_auc_score(
        y_test,
        probabilities,
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
    )

    recall = recall_score(
        y_test,
        predictions,
    )

    f1 = f1_score(
        y_test,
        predictions,
    )

    cm = confusion_matrix(
        y_test,
        predictions,
    )

    metrics = {
        "auc": float(auc),
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": cm.tolist(),
    }

    return metrics


def save_evaluation(metrics, output_dir):
    """
    Save evaluation.json expected by SageMaker ConditionStep.
    """

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    report = {
        "binary_classification_metrics": {
            "auc": {
                "value": metrics["auc"]
            },
            "accuracy": {
                "value": metrics["accuracy"]
            },
            "precision": {
                "value": metrics["precision"]
            },
            "recall": {
                "value": metrics["recall"]
            },
            "f1": {
                "value": metrics["f1"]
            },
        }
    }

    output_path = os.path.join(
        output_dir,
        "evaluation.json",
    )

    with open(output_path, "w") as f:
        json.dump(
            report,
            f,
            indent=4,
        )

    print("\nEvaluation report written to:")
    print(output_path)

    print("\nMetrics")
    print(json.dumps(report, indent=4))

    return output_path


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model-path",
        type=str,
        default="/opt/ml/processing/model/model.pkl",
    )

    parser.add_argument(
        "--test-data",
        type=str,
        default="/opt/ml/processing/test/test.csv",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="/opt/ml/processing/evaluation",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Customer Churn Model Evaluation")
    print("=" * 60)

    model = load_model(args.model_path)

    X_test, y_test = load_test_data(args.test_data)

    metrics = evaluate(
        model,
        X_test,
        y_test,
    )

    save_evaluation(
        metrics,
        args.output_dir,
    )

    print("\nEvaluation completed successfully.")


if __name__ == "__main__":
    main()