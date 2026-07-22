import boto3
import sagemaker

from pipelines.customerchurn.pipeline import get_pipeline

region = boto3.Session().region_name

role = sagemaker.get_execution_role()

pipeline = get_pipeline(
    region=region,
    role=role,
    default_bucket="customer-churn-sm-pipeline",
    model_package_group_name="ChurnModelPackageGroup",
    pipeline_name="ChurnModelPipeline",
)

pipeline.upsert(role_arn=role)

execution = pipeline.start()

print(execution.describe())