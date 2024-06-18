import aws_cdk as cdk
from aws_cdk import (
    Aws,
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_lambda,
)
from constructs import Construct
from cdk_lambda_layer_builder.constructs import BuildPyLayerAsset
import os
from dotenv import load_dotenv
load_dotenv(override=True)

app = cdk.App()
stack = cdk.Stack(app, "AWSCostReport")


class AwsCostReportStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create the pipy layer
        telepot_layer_asset = BuildPyLayerAsset.from_pypi(self, 'telepot-layer',
            pypi_requirements=['telepot', 'python-dotenv'],
            py_runtime=aws_lambda.Runtime.PYTHON_3_8,
            asset_bucket="rio-code-packages"
        )
        telepot_layer = aws_lambda.LayerVersion(
            self,
            id='telepot-layer',
            code=aws_lambda.Code.from_bucket(telepot_layer_asset.asset_bucket, telepot_layer_asset.asset_key),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_8],
            description ='telepot python modules'
        )

        # Definisci la funzione Lambda
        aws_cost_report_lambda = aws_lambda.Function(
            self, 
            "aws-cost-report-lambda",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler='lambda-handler.handler',
            code=aws_lambda.Code.from_asset("aws_cost_report/src"),
            layers=[telepot_layer],
            environment={
                "TOKEN": os.getenv('TOKEN'),
                "USER_ID": os.getenv('USER_ID')
            },
        )

        aws_cost_report_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=["ce:GetCostAndUsage"]
        ))

        # Restrict Lambda to be invoked from own account
        aws_cost_report_lambda.add_permission("invocationRestriction",
            action="lambda:InvokeFunction",
            principal=iam.AccountRootPrincipal(),
            source_account=Aws.ACCOUNT_ID
            )

       
     