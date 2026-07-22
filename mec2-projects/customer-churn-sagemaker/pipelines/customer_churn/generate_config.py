"""
generate_config.py

Customer Churn SageMaker Pipeline

This script generates the configuration files required by
Amazon SageMaker Clarify.

Responsibilities
----------------
1. Read the baseline dataset.
2. Build feature metadata.
3. Specify label information.
4. Configure SHAP explainability.
5. Configure bias detection.
6. Save config.json for the Clarify ProcessingStep.
"""

import argparse
import json
import os

import pandas as pd


# ---------------------------------------------------------
# Feature Metadata
# ---------------------------------------------------------

def build_feature_config(df):
    """
    Generate feature metadata from the baseline dataset.
    """

    features = []

    for column in df.columns:

        feature = {
            "name": str(column),
            "type": "numerical"
        }

        features.append(feature)

    return features


# ---------------------------------------------------------
# Bias Configuration
# ---------------------------------------------------------

def build_bias_config(label_column):
    """
    Configuration used by SageMaker Clarify Bias Report.
    """

    return {

        "label": label_column,

        "facet": None,

        "positive_label": 1,

        "negative_label": 0,

        "methods": [
            "CI",
            "DPL",
            "DPPL",
            "CDDPL",
        ]
    }


# ---------------------------------------------------------
# Explainability Configuration
# ---------------------------------------------------------

def build_shap_config():

    return {

        "method": "kernel_shap",

        "num_samples": 100,

        "agg_method": "mean_abs",

        "save_local_shap_values": True
    }


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--baseline-data",
        default="/opt/ml/processing/input/baseline/baseline.csv",
    )

    parser.add_argument(
        "--output-dir",
        default="/opt/ml/processing/config",
    )

    args = parser.parse_args()

    print("Reading baseline dataset...")

    baseline = pd.read_csv(
        args.baseline_data,
        header=None,
    )

    baseline.columns = [
        f"feature_{i}"
        for i in range(baseline.shape[1])
    ]

    feature_config = build_feature_config(baseline)

    bias_config = build_bias_config(
        label_column="retained"
    )

    shap_config = build_shap_config()

    config = {

        "dataset_type": "text/csv",

        "label": "retained",

        "features": feature_config,

        "bias": bias_config,

        "explainability": shap_config,

        "num_features": len(feature_config)
    }

    os.makedirs(
        args.output_dir,
        exist_ok=True,
    )

    output_file = os.path.join(
        args.output_dir,
        "config.json",
    )

    with open(output_file, "w") as f:

        json.dump(
            config,
            f,
            indent=4,
        )

    print("\nConfiguration generated successfully.")

    print(f"\nSaved to:\n{output_file}")


if __name__ == "__main__":

    main()