# CDK Resources for SCP Management Pipeline

This repository contains the CDK code used for deploying SCP Management Pipeline via CD/CD

## Content

- [Folder Structure](#repository-walk-through)
- [AWS Resources created by the CDK](#aws-resources-created-by-the-cdk)


## Repository walk-through

```sh
.

├── SCP_Management_Pipeline.py            # <-- sets up the main resources required for the SCP pipeline solution.
├── devtools.py                           # <-- sets up the development and deployment tools.
├── pipeline.py                           # <-- the main code that defines all the AWS resources created for building the CI/CD pipeline for SCP creation and management
├── lambda_function                       # <-- contains the lambda function that triggers the SCP management pipeline everytime a change is made in the source code repository of SCPs.
├── terraformbuild_buildspec.yaml         # <-- defines a collection of build commands for the CodeBuild stage - "Terraform validation and plan"
├── access_analyzer_checks_buildspec.yaml # <-- defines a collection of build commands for the CodeBuild stage - "Access Analyzer policy checks"
├── terraform_apply_buildspec.yaml        # <-- defines a collection of build commands for the CodeBuild stage - "Terraform apply"                        
└── README.md                             # <-- This file
```

## AWS Resources created by the CDK

Here are the list of AWS resources created by the CDK code to support the SCP Management Pipeline

1. **SCP-deployment-pipeline** - a Code Pipeline that hosts all the stages of a CI/CD pipeline for managing SCPs. This pipeline contains 5 stages.
    - **Source-Code** - this stage hosts the code that defines the SCPs to be created and the targets of the SCPs
    - **SCP-Plan-Validate** - this stage is to build a plan of all the resources (SCPs and their target attachments) to be created by deploying the code from source repository
    - **IAM-Access-analyzer-checks** - this stage is to perform policy grammer checks, duplication of policy actions and more fine-grained syntax checks in the policy statements
    - **Human-Approval** - this stage is to review the changes made by a security administrator via peer review process
    - **SCP-Deploy** - this stage is to deploy the SCPs in the AWS organization (create / update / delete)

2. **reinforce2024-iam343-tfstate-backend** - an S3 bucket that stores the state information of SCP deployment
3. **SCPManagementPipeline-PipelineCustomResourceProvid-xxxxxxx** - a Lambda function created as a custom CDK resource to upload a zero byte **terraform.tfstate** file in the above mentioned S3 bucket.All SCP state information are store in this .tfstate file.
4. **reinforce2024-iam343-tfstate-lock** - a dynamoDB table that locks the state files of SCP deployment
5. **SCP-Plan-Validate** - a code build project that defines the platform where this stage of the code will run. The build project also includes definition of the *buildspec* file where commands are defined to perform terraform plan and validate commands. 
6. **SCPManagementPipeline-PipelineSCPPlanValidateTerraf--xxxxxxxx** - an IAM service role for the code build stage - SCP-Plan-Validate with an inline policy. This least-privilege access policy grants permission to Code Build to execute all the commands of this build stage
7. **IAM-Access-analyzer-checks** - a code build project that defines the platform where this stage of the code will run. The build project also includes definition of the *buildspec* file where commands are defined to perform IAM Access Analyzer policy grammer, duplication checks. 
8. **SCPManagementPipeline-PipelineIAMACCESSANALYZERCHEC-xxxxxxxx** - an IAM service role for the code build stage - IAM-Access-analyzer-checks with an inline policy. This least-privilege access policy grants permission to Code Build to execute all the commands of this build stage
9. **Human-Approval** - a code build project that triggers a notification to a reviewer of the security administratoion team who verifies the SCP changes are valid.
10. **SCP-Deploy** - a code build project that defines the platform where this stage of the code will run. The build project also includes definition of the *buildspec* file where commands are defined to perform terraform apply.
11. **SCPManagementPipeline-PipelineSCPDeployTerraformapp-xxxxxxxx** - an IAM service role for the code build stage - SCP-Deploy with an inline policy. This least-privilege access policy grants permission to Code Build to execute all the commands of this build stage
12. **SCPManagementPipeline-PipelinePullRequestEvent9EE5E-xxxxxxxxx** - an EventBridge rule that monitors CodeCommit Pull Request State Change and accordingly triggers the pipeline 
13. **SCPManagementPipeline-DevToolsRepositorySCPManageme-xxxxxxxxx** - an EventBridge rule that monitors CodeCommit Repository State Change and accordingly triggers the pipeline 
14. **SCPManagementPipeline-PipelineCustomResourceProvid-xxxxxxxxxxx** - 
15. **SCPManagementPipeline-PipelineTargetForPullRequest-xxxxxxxxxxx** - 
