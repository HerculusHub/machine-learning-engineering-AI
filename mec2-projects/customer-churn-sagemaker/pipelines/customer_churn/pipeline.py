"""
pipeline.py

Creates the complete SageMaker Pipeline for the
Customer Churn Project.

Pipeline Flow

Raw Data
    │
    ▼
Preprocess
    │
    ▼
Hyperparameter Tuning
    │
    ▼
Evaluation
    │
    ▼
Condition (AUC >= threshold?)
    │
 ┌──┴───────────────┐
 │                  │
 ▼                  ▼
Stop             Register Model
                     │
                     ▼
               Create Model
                     │
                     ▼
               Batch Transform
                     │
                     ▼
             Generate Config
                     │
                     ▼
                 SageMaker Clarify
"""

from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import PipelineSession

from pipelines.customerchurn.steps import (
    create_processing_step,
    create_tuning_step,
    create_evaluation_step,
    create_condition_step,
    create_register_step,
    create_model_step,
    create_transform_step,
    create_generate_config_step,
    create_clarify_step,
)

def get_pipeline(
    region,
    role,
    default_bucket,
    model_package_group_name,
    pipeline_name,
    custom_image_uri,
    sklearn_processor_version="0.23-1",
):
    pipeline_session = PipelineSession()

    processing_instance_type = "ml.m5.xlarge"
    processing_instance_count = 1

    training_instance_type = "ml.m5.xlarge"

    auc_threshold = 0.75

    process_step = create_processing_step(
        role=role,
        pipeline_session=pipeline_session,
        default_bucket=default_bucket,
        sklearn_processor_version=sklearn_processor_version,
        processing_instance_type=processing_instance_type,
        processing_instance_count=processing_instance_count,
    )

    estimator, tuning_step = create_tuning_step(
        role=role,
        pipeline_session=pipeline_session,
        process_step=process_step,
        training_instance_type=training_instance_type,
    )

    evaluation_step = create_evaluation_step(
        role=role,
        pipeline_session=pipeline_session,
        sklearn_processor_version=sklearn_processor_version,
        processing_instance_type=processing_instance_type,
        processing_instance_count=processing_instance_count,
        process_step=process_step,
        tuning_step=tuning_step,
    )

    register_step = create_register_step(
        estimator=estimator,
        tuning_step=tuning_step,
        model_package_group_name=model_package_group_name,
        model_approval_status="PendingManualApproval",
    )
    create_model_step = create_model_step(
        role=role,
        pipeline_session=pipeline_session,
        tuning_step=tuning_step,
    )
    transform_step = create_transform_step(
        model=create_model_step,
        batch_data=f"s3://{default_bucket}/data/batch/batch.csv",
    )

    config_step = create_generate_config_step(
        role=role,
        pipeline_session=pipeline_session,
        sklearn_processor_version=sklearn_processor_version,
        processing_instance_type=processing_instance_type,
        processing_instance_count=processing_instance_count,
    )

    clarify_step = create_clarify_step(
        role=role,
        model_name=create_model_step,
        baseline_data=f"s3://{default_bucket}/input/baseline/baseline.csv",
        config_uri=config_step.properties.ProcessingOutputConfig
        .Outputs["config"]
        .S3Output.S3Uri,
    )

    condition_step = create_condition_step(
        evaluation_step=evaluation_step,
        auc_threshold=auc_threshold,
        if_steps=[
            register_step,
            create_model_step,
            transform_step,
            config_step,
            clarify_step,
        ],
    )

    pipeline = Pipeline(
        name=pipeline_name,
        parameters=[],
        steps=[
            process_step,
            tuning_step,
            evaluation_step,
            condition_step,
        ],
        sagemaker_session=pipeline_session,
    )

    return pipeline
