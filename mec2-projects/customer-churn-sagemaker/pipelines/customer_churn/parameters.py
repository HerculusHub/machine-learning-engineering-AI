"""
Pipeline Parameters

Defines every SageMaker Pipeline parameter used throughout the
Customer Churn Pipeline.

These parameters can be overridden when the pipeline is executed.

Compatible with SageMaker SDK v2.x
Compatible with XGBoost 0.90-2
"""

from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterFloat,
    ParameterString,
)


# ------------------------------------------------------------------
# Processing Parameters
# ------------------------------------------------------------------

processing_instance_count = ParameterInteger(
    name="ProcessingInstanceCount",
    default_value=1,
)

processing_instance_type = ParameterString(
    name="ProcessingInstanceType",
    default_value="ml.m5.xlarge",
)


# ------------------------------------------------------------------
# Training Parameters
# ------------------------------------------------------------------

training_instance_count = ParameterInteger(
    name="TrainingInstanceCount",
    default_value=1,
)

training_instance_type = ParameterString(
    name="TrainingInstanceType",
    default_value="ml.m5.xlarge",
)


# ------------------------------------------------------------------
# Batch Transform Parameters
# ------------------------------------------------------------------

transform_instance_count = ParameterInteger(
    name="TransformInstanceCount",
    default_value=1,
)

transform_instance_type = ParameterString(
    name="TransformInstanceType",
    default_value="ml.m5.large",
)


# ------------------------------------------------------------------
# Model Registry
# ------------------------------------------------------------------

model_approval_status = ParameterString(
    name="ModelApprovalStatus",
    default_value="PendingManualApproval",
)


# ------------------------------------------------------------------
# Evaluation Threshold
# ------------------------------------------------------------------

auc_threshold = ParameterFloat(
    name="AUCThreshold",
    default_value=0.80,
)


# ------------------------------------------------------------------
# Input Dataset
# ------------------------------------------------------------------

input_data = ParameterString(
    name="InputDataUrl",
    default_value="",
)


# ------------------------------------------------------------------
# Batch Transform Dataset
# ------------------------------------------------------------------

batch_data = ParameterString(
    name="BatchDataUrl",
    default_value="",
)


# ------------------------------------------------------------------
# Baseline Dataset (Clarify)
# ------------------------------------------------------------------

baseline_data = ParameterString(
    name="BaselineDataUrl",
    default_value="",
)


# ------------------------------------------------------------------
# Output Prefix
# ------------------------------------------------------------------

output_prefix = ParameterString(
    name="OutputPrefix",
    default_value="output",
)


# ------------------------------------------------------------------
# Processing Output Prefix
# ------------------------------------------------------------------

processing_output_prefix = ParameterString(
    name="ProcessingOutputPrefix",
    default_value="processing",
)


# ------------------------------------------------------------------
# Pipeline Name
# ------------------------------------------------------------------

pipeline_name = ParameterString(
    name="PipelineName",
    default_value="CustomerChurnPipeline",
)


# ------------------------------------------------------------------
# Model Package Group
# ------------------------------------------------------------------

model_package_group_name = ParameterString(
    name="ModelPackageGroupName",
    default_value="ChurnModelPackageGroup",
)


# ------------------------------------------------------------------
# Random Seed
# ------------------------------------------------------------------

random_seed = ParameterInteger(
    name="RandomSeed",
    default_value=42,
)


# ------------------------------------------------------------------
# Hyperparameter Tuning
# ------------------------------------------------------------------

max_training_jobs = ParameterInteger(
    name="MaxTrainingJobs",
    default_value=20,
)

max_parallel_training_jobs = ParameterInteger(
    name="MaxParallelTrainingJobs",
    default_value=3,
)


# ------------------------------------------------------------------
# XGBoost Parameters
# ------------------------------------------------------------------

objective = ParameterString(
    name="Objective",
    default_value="binary:logistic",
)

eval_metric = ParameterString(
    name="EvalMetric",
    default_value="auc",
)


# ------------------------------------------------------------------
# Collection of all pipeline parameters
# ------------------------------------------------------------------

PIPELINE_PARAMETERS = [

    processing_instance_count,
    processing_instance_type,

    training_instance_count,
    training_instance_type,

    transform_instance_count,
    transform_instance_type,

    model_approval_status,

    auc_threshold,

    input_data,

    batch_data,

    baseline_data,

    output_prefix,

    processing_output_prefix,

    pipeline_name,

    model_package_group_name,

    random_seed,

    max_training_jobs,

    max_parallel_training_jobs,

    objective,

    eval_metric,

]