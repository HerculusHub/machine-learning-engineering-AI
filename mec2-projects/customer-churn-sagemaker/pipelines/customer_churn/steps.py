"""
Customer Churn SageMaker Pipeline Steps

Compatible with:

    SageMaker SDK v2
    XGBoost 0.90-2

This module creates every SageMaker Pipeline step.
"""

import os

from sagemaker.processing import (
    ProcessingInput,
    ProcessingOutput,
)

from sagemaker.sklearn.processing import SKLearnProcessor

from sagemaker.estimator import Estimator

from sagemaker.inputs import TrainingInput

from sagemaker.tuner import (
    HyperparameterTuner,
    ContinuousParameter,
    IntegerParameter,
)

from sagemaker.workflow.steps import (
    ProcessingStep,
    TuningStep,
)

from sagemaker.workflow.properties import PropertyFile

from sagemaker.workflow.functions import JsonGet

from sagemaker.workflow.condition_step import ConditionStep

from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo

from sagemaker.workflow.model_step import (
    RegisterModel,
    CreateModelStep,
)

from sagemaker.transformer import Transformer

from sagemaker.workflow.steps import TransformStep

from sagemaker.model import Model

from sagemaker.workflow.step_collections import ClarifyCheckStep

from sagemaker.model_metrics import (
    MetricsSource,
    ModelMetrics,
)

from sagemaker.workflow.pipeline_context import PipelineSession


def create_processing_step(

    role,

    default_bucket,

    pipeline_session,

    sklearn_processor_version,

    processing_instance_type,

    processing_instance_count,

    input_data,

):
    """
    Preprocess raw customer data.

    Outputs

        train.csv

        validation.csv

        test.csv
    """

    processor = SKLearnProcessor(

        framework_version=sklearn_processor_version,

        role=role,

        instance_type=processing_instance_type,

        instance_count=processing_instance_count,

        sagemaker_session=pipeline_session,

    )

    step = ProcessingStep(

        name="ChurnModelProcess",

        processor=processor,

        inputs=[

            ProcessingInput(

                source=input_data,

                destination="/opt/ml/processing/input",

            )

        ],

        outputs=[

            ProcessingOutput(

                output_name="train",

                source="/opt/ml/processing/train",

            ),

            ProcessingOutput(

                output_name="validation",

                source="/opt/ml/processing/validation",

            ),

            ProcessingOutput(

                output_name="test",

                source="/opt/ml/processing/test",

            ),

        ],

        code="pipelines/customerchurn/preprocess.py",

    )

    return step

def create_xgboost_estimator(

    role,

    pipeline_session,

    training_instance_type,

    training_instance_count,

):
    """
    Build XGBoost estimator.
    """

    estimator = Estimator(

        image_uri=
        "683313688378.dkr.ecr.us-east-1.amazonaws.com/"
        "sagemaker-xgboost:0.90-2-cpu-py3",

        role=role,

        instance_count=training_instance_count,

        instance_type=training_instance_type,

        volume_size=30,

        max_run=3600,

        output_path="s3://{}/model".format(
            pipeline_session.default_bucket()
        ),

        sagemaker_session=pipeline_session,

    )

    estimator.set_hyperparameters(

        objective="binary:logistic",

        eval_metric="auc",

        num_round=200,

    )

    return estimator
def create_hyperparameter_ranges():

    ranges = {

        "eta": ContinuousParameter(
            0.01,
            0.3,
        ),

        "max_depth": IntegerParameter(
            3,
            10,
        ),

        "min_child_weight": IntegerParameter(
            1,
            10,
        ),

        "subsample": ContinuousParameter(
            0.5,
            1.0,
        ),

        "colsample_bytree": ContinuousParameter(
            0.5,
            1.0,
        ),

        "gamma": ContinuousParameter(
            0,
            5,
        ),

    }

    return ranges
def create_tuning_step(

    role,

    pipeline_session,

    training_instance_type,

    training_instance_count,

    process_step,

):
    """
    Hyperparameter Optimization.
    """

    estimator = create_xgboost_estimator(

        role,

        pipeline_session,

        training_instance_type,

        training_instance_count,

    )

    tuner = HyperparameterTuner(

        estimator=estimator,

        objective_metric_name="validation:auc",

        objective_type="Maximize",

        hyperparameter_ranges=
        create_hyperparameter_ranges(),

        metric_definitions=[

            {

                "Name": "validation:auc",

                "Regex": "validation-auc: ([0-9\\.]+)",

            }

        ],

        max_jobs=20,

        max_parallel_jobs=3,

    )

    tuning_step = TuningStep(

        name="ChurnHyperParameterTuning",

        tuner=tuner,

        inputs={

            "train": TrainingInput(

                s3_data=
                process_step.properties.ProcessingOutputConfig
                .Outputs["train"]
                .S3Output
                .S3Uri,

                content_type="text/csv",

            ),

            "validation": TrainingInput(

                s3_data=
                process_step.properties.ProcessingOutputConfig
                .Outputs["validation"]
                .S3Output
                .S3Uri,

                content_type="text/csv",

            ),

        },

    )

    return tuning_step
# ------------------------------------------------------------
# Evaluation Report Property File
# ------------------------------------------------------------

evaluation_report = PropertyFile(
    name="ChurnEvaluationReport",
    output_name="evaluation",
    path="evaluation.json",
)
def create_evaluation_step(
    role,
    pipeline_session,
    sklearn_processor_version,
    processing_instance_type,
    processing_instance_count,
    process_step,
    tuning_step,
):
    """
    Evaluate the best XGBoost model on the test dataset.
    """

    processor = SKLearnProcessor(
        framework_version=sklearn_processor_version,
        role=role,
        instance_type=processing_instance_type,
        instance_count=processing_instance_count,
        sagemaker_session=pipeline_session,
    )

    step = ProcessingStep(
        name="ChurnEvalBestModel",
        processor=processor,
        inputs=[
            ProcessingInput(
                source=tuning_step.get_top_model_s3_uri(
                    top_k=0,
                    s3_bucket=pipeline_session.default_bucket(),
                ),
                destination="/opt/ml/processing/model",
            ),
            ProcessingInput(
                source=process_step.properties.ProcessingOutputConfig
                .Outputs["test"]
                .S3Output.S3Uri,
                destination="/opt/ml/processing/test",
            ),
        ],
        outputs=[
            ProcessingOutput(
                output_name="evaluation",
                source="/opt/ml/processing/evaluation",
            )
        ],
        code="pipelines/customerchurn/evaluate.py",
        property_files=[evaluation_report],
    )

    return step
def create_condition_step(
    evaluation_step,
    auc_threshold,
    if_steps,
):
    """
    Continue only if AUC exceeds threshold.
    """

    return ConditionStep(
        name="CheckAUCScoreChurnEvaluation",
        conditions=[
            ConditionGreaterThanOrEqualTo(
                left=JsonGet(
                    step_name=evaluation_step.name,
                    property_file=evaluation_report,
                    json_path="metrics.auc.value",
                ),
                right=auc_threshold,
            )
        ],
        if_steps=if_steps,
        else_steps=[],
    )
def create_register_step(
    estimator,
    tuning_step,
    model_package_group_name,
    model_approval_status,
):
    """
    Register best model in SageMaker Model Registry.
    """

    model_metrics = ModelMetrics(
        model_statistics=MetricsSource(
            s3_uri=evaluation_report,
            content_type="application/json",
        )
    )

    return RegisterModel(
        name="RegisterChurnModel",
        estimator=estimator,
        model_data=tuning_step.get_top_model_s3_uri(
            top_k=0,
        ),
        content_types=["text/csv"],
        response_types=["text/csv"],
        inference_instances=[
            "ml.m5.large",
        ],
        transform_instances=[
            "ml.m5.large",
        ],
        model_package_group_name=model_package_group_name,
        approval_status=model_approval_status,
        model_metrics=model_metrics,
    )
def create_model_step(
    role,
    pipeline_session,
    tuning_step,
):
    """
    Create SageMaker model.
    """

    model = Model(
        image_uri="683313688378.dkr.ecr.us-east-1.amazonaws.com/"
                  "sagemaker-xgboost:0.90-2-cpu-py3",
        model_data=tuning_step.get_top_model_s3_uri(
            top_k=0
        ),
        role=role,
        sagemaker_session=pipeline_session,
    )

    return CreateModelStep(
        name="ChurnCreateModel",
        model=model,
    )
def create_transform_step(
    model,
    batch_data,
):
    """
    Batch prediction.
    """

    transformer = Transformer(
        model_name=model.properties.ModelName,
        instance_type="ml.m5.large",
        instance_count=1,
        output_path="s3://batch-output",
    )

    return TransformStep(
        name="ChurnTransform",
        transformer=transformer,
        inputs=batch_data,
    )
def create_generate_config_step(
    role,
    pipeline_session,
    sklearn_processor_version,
    processing_instance_type,
    processing_instance_count,
):
    """
    Generate Clarify configuration.
    """

    processor = SKLearnProcessor(
        framework_version=sklearn_processor_version,
        role=role,
        instance_type=processing_instance_type,
        instance_count=processing_instance_count,
        sagemaker_session=pipeline_session,
    )

    return ProcessingStep(
        name="ChurnModelConfigFile",
        processor=processor,
        outputs=[
            ProcessingOutput(
                output_name="config",
                source="/opt/ml/processing/output",
            )
        ],
        code="pipelines/customerchurn/generate_config.py",
    )
def create_clarify_step(
    role,
    model_name,
    baseline_data,
    config_uri,
):
    """
    Model Explainability and Bias Detection.
    """

    return ClarifyCheckStep(
        name="ClarifyProcessingStep",
        clarify_check_config=config_uri,
        model_config=model_name,
        skip_check=False,
        register_new_baseline=True,
    )
