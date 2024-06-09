from constructs import Construct
import aws_cdk as cdk
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import aws_s3 as s3

class DevTools(Construct):

    @property
    def code_repo(self):
        return self._code_repo
        
    @property
    def config_bucket(self):
        return self._config_bucket

    def __init__(self, scope: Construct, id: str, config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        ### CodeCommit - code repo
        self._code_repo = codecommit.Repository(
            self, "Repository",
            repository_name="SCP-management-pipeline",
            code=codecommit.Code.from_directory("./source_code/"),
            description="Deploys SCPs")
        
        ### S3 Bucket
        self._config_bucket = s3.Bucket(
            self, "PipelineConfigBucket",
            enforce_ssl=True,
            removal_policy=cdk.RemovalPolicy.DESTROY
            )
            
        ### Outputs
        self.output_codecommit_repo = cdk.CfnOutput(
            self, "CodeCommitRepo",
            value=self._code_repo.repository_name,
            description="AWS CodeCommit repository for hosting project source code"
            )   
        
        self.output_s3_bucket = cdk.CfnOutput(
            self, "ConfigBucket",
            value=self._config_bucket.bucket_name,
            description="S3 bucket to store reference policy and actions list",
            )    
