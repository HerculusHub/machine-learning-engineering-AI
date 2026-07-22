import json

from pipelines.customerchurn.pipeline import get_pipeline

import boto3
import sagemaker

region = boto3.Session().region_name

role = sagemaker.get_execution_role()

pipeline = get_pipeline(
    region=region,
    role=role,
    default_bucket="customer-churn-sm-pipeline",
    model_package_group_name="ChurnModelPackageGroup",
    pipeline_name="ChurnModelPipeline",
)

definition = pipeline.definition()

with open("pipeline_definition.json", "w") as f:

    f.write(definition)

print("Pipeline definition saved.")