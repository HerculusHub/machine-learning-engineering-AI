import boto3
import sagemaker


def get_region():

    return boto3.Session().region_name


def get_session(region=None):

    if region is None:
        region = get_region()

    boto_session = boto3.Session(region_name=region)

    return sagemaker.Session(
        boto_session=boto_session
    )


def get_execution_role():

    try:
        return sagemaker.get_execution_role()

    except Exception:
        iam = boto3.client("iam")

        return iam.get_role(
            RoleName="AmazonSageMakerExecutionRole"
        )["Role"]["Arn"]