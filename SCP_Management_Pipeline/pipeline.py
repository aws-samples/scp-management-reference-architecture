import boto3
import os

from constructs import Construct
import aws_cdk as cdk
import aws_cdk.pipelines as pipelines
from aws_cdk.pipelines import ManualApprovalStep
from cdk_nag import NagSuppressions, NagPackSuppression
from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_lambda as awslambda,
    aws_events as events,
    aws_events_targets as events_targets,
    aws_iam as iam,
    aws_sns as sns,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    custom_resources as cr
)

REGION = boto3.session.Session().region_name

class Pipeline(Construct):

    def __init__(self, scope: Construct, id: str, devtools, config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        ### CodePipeline
        pipeline = codepipeline.Pipeline(
            self, "Pipeline",
            pipeline_name="SCP-deployment-pipeline",
            stages=[]
        )

        ### Define source Stage
        source_output = codepipeline.Artifact()
        pipeline.add_stage(
            stage_name="Source-Code",
            actions=[
                codepipeline_actions.CodeCommitSourceAction(
                    action_name="CodeCommit",
                    branch="main",
                    repository=devtools.code_repo,
                    output=source_output,
                    run_order=1
                )
            ]
        )

        tfstate_bucket = s3.Bucket(
            self, "tfstate-backend-bucket",
            bucket_name="reinforce2024-iam343-tfstate-backend",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            object_ownership=s3.ObjectOwnership.OBJECT_WRITER,
            access_control=s3.BucketAccessControl.PRIVATE,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # Define a Lambda function to create and upload terraform.tfstate to S3 bucket
        lambda_function_create_tfstate = awslambda.Function(
            self, "CreateTfStateFunction",
            code=awslambda.Code.from_inline("""
import json
import boto3
import os

def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        bucket_name = os.environ['BUCKET_NAME']
        key = 'terraform.tfstate'
        content = ''

        s3.put_object(Bucket=bucket_name, Key=key, Body=content)
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully created and uploaded terraform.tfstate')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
            """),
            handler="index.lambda_handler",
            runtime=awslambda.Runtime.PYTHON_3_8,
            environment={
                "BUCKET_NAME": tfstate_bucket.bucket_name
            }
        )

        # Grant the Lambda function permission to write to the S3 bucket
        tfstate_bucket.grant_write(lambda_function_create_tfstate)

        # Create custom resource provider
        provider = cr.Provider(
            self, "CustomResourceProvider",
            on_event_handler=lambda_function_create_tfstate
        )

        # Create custom resource
        custom_resource = cdk.CustomResource(
            self, "CreateTfStateCustomResource",
            service_token=provider.service_token,
            properties={
                "bucket_name": tfstate_bucket.bucket_name,
                "key": "terraform.tfstate",
                "content": ""  # Empty JSON content
            }
        )

        # Define a DynamoDB table to lock the state file
        tflock_table = dynamodb.Table(
            self, "tfstate-lock-table",
            table_name="reinforce2024-iam343-tfstate-lock",
            partition_key=dynamodb.Attribute(name="LockID", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PROVISIONED,  # Use billing_mode instead of billing
            encryption=dynamodb.TableEncryption.AWS_MANAGED,  # Use TableEncryption.AWS_MANAGED instead of TableEncryptionV2
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # Set provisioned capacity for read and write
        tflock_table.auto_scale_read_capacity(
            min_capacity=20,
            max_capacity=20
        )
        tflock_table.auto_scale_write_capacity(
            min_capacity=20,
            max_capacity=20
        )

        ### Terraform build
        security_ci = pipeline.add_stage(
            stage_name="SCP-Plan-Validate"
        )

        Terraformplan = codebuild.PipelineProject(
            self, "Terraformplan",
            project_name="SCP-Plan-Validate",
            build_spec=codebuild.BuildSpec.from_asset("./SCP_Management_Pipeline/terraformbuild_buildspec.yaml"),
            environment=codebuild.BuildEnvironment(
                privileged=False,
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_3
            ),
            description="Build",
            timeout=cdk.Duration.minutes(60)
        )

        ### Define role permissions for Terraformplan checks
        Terraformplan.role.attach_inline_policy(iam.Policy(self, "TerraformplanInlinePolicy",
            document=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement( 
                        actions=[
                            "organizations:DescribeOrganization",
                            "organizations:ListAccounts",
                            "organizations:ListRoots",
                            "organizations:ListAWSServiceAccessForOrganization",
                            "organizations:DescribePolicy",
				            "organizations:TagResource",
				            "organizations:UntagResource",
				            "organizations:ListPoliciesForTarget",
				            "organizations:ListTargetsForPolicy",
				            "organizations:ListPolicies",
                            "organizations:ListTagsForResource"
                        ],
                        resources=["*"]
                    ),
                    iam.PolicyStatement( 
                        actions=["logs:*"],
                        resources=["arn:aws:logs:*:*:*"]
                    ),
                    iam.PolicyStatement( 
                        actions=[
                            "s3:List*",
                            "s3:Get*",
                            "s3:Put*",
                            "s3:DeleteObject",
                            "s3:DeleteObjectVersion"
                        ],
                        resources=[
                            f"{tfstate_bucket.bucket_arn}",
                            f"{tfstate_bucket.bucket_arn}/*"
                        ]
                    ),
                    iam.PolicyStatement( 
                        actions=[
                            "dynamodb:BatchGetItem",
                            "dynamodb:Query",
                            "dynamodb:PutItem",
                            "dynamodb:UpdateItem",
                            "dynamodb:DeleteItem",
                            "dynamodb:BatchWriteItem",
                            "dynamodb:Describe*",
                            "dynamodb:Get*",
                            "dynamodb:List*"
                        ],
                        resources=[f"{tflock_table.table_arn}"]
                    )
                ]
        )
        ))

        security_ci.add_action(
            codepipeline_actions.CodeBuildAction(
                action_name="Terraform-plan-validate",
                input=source_output,
                project=Terraformplan,
                run_order=1
            )
        )

        ### Access analyzer checks only work if files are json format and dont allow variables, check the buildspec file 
        ### Transform policy stage
        security_ci = pipeline.add_stage(
            stage_name="IAM-Access-analyzer-checks"
        )

        ### Define check policy grammar and syntax
        accessanalyzerchecks = codebuild.PipelineProject(
            self, "IAMACCESSANALYZERCHECKS",
            project_name="IAM-Access-analyzer-checks",
            build_spec=codebuild.BuildSpec.from_asset("./SCP_Management_Pipeline/access_analyzer_checks_buildspec.yaml"),
            environment=codebuild.BuildEnvironment(
                privileged=False,
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_3
            ),
            description="Policy grammar and syntax checks",
            timeout=cdk.Duration.minutes(60)
        )

        ### Define role permissions for access analyzer checks
        accessanalyzerchecks.role.attach_inline_policy(iam.Policy(self, "ACCESSANALYZERCHECKSInlinePolicy",
            document=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement( 
                        actions=[
                            "access-analyzer:ValidatePolicy",
                            "iam:GetPolicy",
                            "iam:GetPolicyVersion"
                        ],
                        resources=["*"]
                    ), 
                    iam.PolicyStatement( 
                        actions=[
                            "organizations:DescribeOrganization",
                            "organizations:ListAccounts",
                            "organizations:ListRoots",
                            "organizations:ListAWSServiceAccessForOrganization",
                            "organizations:DescribePolicy",
				            "organizations:TagResource",
				            "organizations:UntagResource",
				            "organizations:ListPoliciesForTarget",
				            "organizations:ListTargetsForPolicy",
				            "organizations:ListPolicies",
                            "organizations:ListTagsForResource"
                        ],
                        resources=["*"]
                    ), 
                    iam.PolicyStatement( 
                        actions=["s3:getObject"], 
                        resources=["*"]
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "codecommit:PostCommentForPullRequest", 
                            "codecommit:UpdatePullRequestStatus", 
                            "codecommit:GitPull" 
                        ],
                        resources=[devtools.code_repo.repository_arn]
                    ),
                    iam.PolicyStatement(
                        actions=["iam:CreateServiceLinkedRole"],
                        resources=["*"],
                        conditions={
                            "StringEquals": {
                                "iam:AWSServiceName": "access-analyzer.amazonaws.com"
                            }
                        }
                    ),
                    iam.PolicyStatement( 
                        actions=["logs:*"],
                        resources=["arn:aws:logs:*:*:*"]
                    ),
                    iam.PolicyStatement( 
                        actions=[
                            "s3:List*",
                            "s3:Get*",
                            "s3:Put*",
                            "s3:DeleteObject",
                            "s3:DeleteObjectVersion"
                        ],
                        resources=[
                            f"{tfstate_bucket.bucket_arn}",
                            f"{tfstate_bucket.bucket_arn}/*"
                        ]
                    ),
                    iam.PolicyStatement( 
                        actions=[
                            "dynamodb:BatchGetItem",
                            "dynamodb:Query",
                            "dynamodb:PutItem",
                            "dynamodb:UpdateItem",
                            "dynamodb:DeleteItem",
                            "dynamodb:BatchWriteItem",
                            "dynamodb:Describe*",
                            "dynamodb:Get*",
                            "dynamodb:List*"
                        ],
                        resources=[f"{tflock_table.table_arn}"]
                    )
                ]
        )
        ))


        ### Add iam access analyzer checks action to pipeline
        security_ci.add_action(
            codepipeline_actions.CodeBuildAction(
                action_name="IAM-Access-analyzer-checks",
                input=source_output,
                project=accessanalyzerchecks,
                run_order=3
            )
        )

        sns_topic = sns.Topic.from_topic_arn(self, "SCPApprovalTopic", config.get("SNSarn"))
        review_url = f"https://{REGION}.console.aws.amazon.com/codesuite/codecommit/repositories/SCP-management-pipeline/browse?region={REGION}"

        ### Define Manual Approval Stage
        human_approval_stage = pipeline.add_stage(
            stage_name="Human-Approval"
        )

        human_approval_action = codepipeline_actions.ManualApprovalAction(
            action_name="ReviewerApprovalAction",
            notification_topic=sns_topic,
            additional_information=review_url
        )
        human_approval_stage.add_action(human_approval_action)

        ## Add deploy stage to Pipeline
        ##
        security_ci = pipeline.add_stage(
            stage_name="SCP-Deploy"
        )

        Terraformdeploy = codebuild.PipelineProject(
            self, "TERRAFORM-DEPLOY",
            project_name="SCP-Deploy",
            build_spec=codebuild.BuildSpec.from_asset("./SCP_Management_Pipeline/terraform_apply_buildspec.yaml"),
            environment=codebuild.BuildEnvironment(
                privileged=False,
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_3
            ),
            description="Deploy",
            timeout=cdk.Duration.minutes(60)
        )

        ### Define role permissions for terraform deploy
        Terraformdeploy.role.attach_inline_policy(iam.Policy(self, "TERRAFORMDEPLOYInlinePolicy",
            document=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement( 
                        actions=[
                            "organizations:ListTagsForResource",
				            "organizations:CreatePolicy",
				            "organizations:DeletePolicy",
				            "organizations:DescribeOrganization",
				            "organizations:DescribePolicy",
				            "organizations:ListAWSServiceAccessForOrganization",
				            "organizations:ListAccounts",
				            "organizations:ListRoots",
				            "organizations:TagResource",
				            "organizations:UntagResource",
				            "organizations:UpdatePolicy",
				            "organizations:AttachPolicy",
                            "organizations:DetachPolicy",
				            "organizations:ListPoliciesForTarget",
				            "organizations:ListTargetsForPolicy",
				            "organizations:ListPolicies"
                        ],
                        resources=["*"]
                    ),
                    iam.PolicyStatement( 
                        actions=["logs:*"],
                        resources=["arn:aws:logs:*:*:*"]
                    ),
                    iam.PolicyStatement( 
                        actions=[
                            "s3:List*",
                            "s3:Get*",
                            "s3:Put*",
                            "s3:DeleteObject",
                            "s3:DeleteObjectVersion"
                        ],
                        resources=[
                            f"{tfstate_bucket.bucket_arn}",
                            f"{tfstate_bucket.bucket_arn}/*"
                        ]
                    ),
                    iam.PolicyStatement( 
                        actions=[
                            "dynamodb:BatchGetItem",
                            "dynamodb:Query",
                            "dynamodb:PutItem",
                            "dynamodb:UpdateItem",
                            "dynamodb:DeleteItem",
                            "dynamodb:BatchWriteItem",
                            "dynamodb:Describe*",
                            "dynamodb:Get*",
                            "dynamodb:List*"
                        ],
                        resources=[f"{tflock_table.table_arn}"]
                    )
            ]
        )
        ))

        security_ci.add_action(
            codepipeline_actions.CodeBuildAction(
                action_name="Terraform-apply",
                input=source_output,
                project=Terraformdeploy,
                run_order=5
            )
        )



        # Add event bridge rule to trigger codepipline based on pull request 
        rule = events.Rule( 
            self, "PullRequestEvent",
            description="Trigger Pipeline on Pull Request",
            event_pattern=events.EventPattern(
                source=["aws.codecommit"],
                detail_type=["CodeCommit Pull Request State Change"],
                resources=[devtools.code_repo.repository_arn],
                detail={ 
                    "destinationReference": ["refs/heads/main"],
                    "event": ["pullRequestCreated"]
                    }
                )
        )

        ### Define lambda function to trigger pipeline based on event bridge rule
        lambda_function = awslambda.Function(
            self, "TargetForPullRequests",
            code=awslambda.Code.from_asset("./SCP_Management_Pipeline/lambda_function"),
            handler="lambda_function.lambda_handler",
            runtime=awslambda.Runtime.PYTHON_3_11,
            environment={
                "Terraformplan_PROJECT_NAME": Terraformplan.project_name,
                "ACCESSANALYZERCHECKS_PROJECT_NAME": accessanalyzerchecks.project_name,
                "TERRAFORMDEPLOY_PROJECT_NAME": Terraformdeploy.project_name,
            }
        )

        ### Define role permissions for Lambda function
        lambda_function.add_to_role_policy(iam.PolicyStatement(
            actions=["codebuild:StartBuild"],
            resources=[Terraformplan.project_arn, accessanalyzerchecks.project_arn, Terraformdeploy.project_arn]
        ))

        NagSuppressions.add_resource_suppressions(lambda_function,[{
            'id': 'AwsSolutions-IAM4', 'reason': 'supressing since it only allows your lambda permissions to write logs'
        }],apply_to_children=True,)

        rule.add_target(events_targets.LambdaFunction(lambda_function))
