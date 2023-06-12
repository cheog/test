"""An AWS Python Pulumi program"""

from json import dumps
from pathlib import Path
from tempfile import TemporaryDirectory

import pulumi
from pulumi_aws import iam, lambda_, s3

from src.package_lambda import package_lambda

# Create an AWS resource (S3 Bucket)
bucket = s3.Bucket("my-bucket")

lambda_role = iam.Role(
    "lambda-role",
    assume_role_policy=dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "lambda.amazonaws.com",
                    },
                    "Effect": "Allow",
                }
            ],
        }
    ),
    managed_policy_arns=[iam.ManagedPolicy.AWS_LAMBDA_EXECUTE],
)

tmp_dir_name = TemporaryDirectory()
tmp_dir = Path(tmp_dir_name.name)
code = package_lambda(Path("../../service"), Path("../../service/me_thing"), tmp_dir)
aws_lambda = lambda_.Function(
    "me-funky",
    code=code,
    runtime="python3.10",
    handler="main.main",
    environment={"variables": {"BUCKET": bucket.id}},
    role=lambda_role.arn,
)

# Export the name of the bucket
pulumi.export("bucket_name", bucket.id)
pulumi.export("lambda_name", aws_lambda.id)
