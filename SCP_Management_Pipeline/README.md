# CDK Resources for SCP Management Pipeline

This repository contains the CDK code used for deploying SCP Management Pipeline via CD/CD

## Content

- [Folder Structure](#repository-walk-through)
- [Prerequisites ](#prerequisites)
- [Deployment Instructions](#deployment-instructions)
  - [Pipeline Deployment using CDK](#pipeline-deployment-using-cdk)
    - [Steps to follow:](#steps-to-follow)
    - [Cleanup:](#cleanup)
  - [SCPs Deployment through your chosen pipeline](#scps-deployment-through-your-chosen-pipeline)

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

Before getting started, 
* Create a pre-configured [Amazon SNS topic with atleast one verified subscriber](https://docs.aws.amazon.com/sns/latest/dg/sns-create-topic.html).
    - This SNS topic is needed for notifying the reviewer for any change in the SCP management via email notification.
    - As an email subscriber for SNS topic need manual verification hence for the ease of deployment this step is requested as a pre-requisite for this solution
    - You can customize this notification step as per your organization requirement and also include it in the pipeline deployment code.
* AWS Organizations must be enabled with multiple organization units (OUs).
    - This solution is applicable only for those AWS environment which has a multi-account environment divided into multiple OUs

Basic understating of the following can help as this solution uses: 
* Python and [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html).
* [CDK environments](https://docs.aws.amazon.com/cdk/v2/guide/environments.html).
* [Getting started with Terraform for AWS](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)
* [Terraform: Beyond the Basics with AWS](https://aws.amazon.com/blogs/apn/terraform-beyond-the-basics-with-aws/)

## Deployment Instructions

### Pipeline Deployment using CDK

#### Steps to follow
1. Use the following command to download this Cloud Development Kit (CDK) project in your environment.

    ```git clone https://github.com/aws-samples/scp-management-reference-architecture```
    
2. Create a virtual Python environment to contain the project dependencies by using the following command.

    ```python3 -m venv .venv```

3. Activate the virtual environment with the following command.

    ```source .venv/bin/activate```

4. Install the project requirements by using the following command.

    ```pip install -r requirements.txt```

5. Use the following command to update the CDK CLI to the latest major version.

    ```npm install -g aws-cdk@2 --force```

6. Before you can deploy the CDK project, use the following command to bootstrap your AWS environment. Bootstrapping is the process of creating resources needed for deploying CDK projects. These resources include an Amazon Simple Storage Service (Amazon S3) bucket for storing files and IAM roles that grant permissions needed to perform deployments.

    ```cdk bootstrap```

7. Finally, use the following command to deploy the pipeline infrastructure. Replace SNS arn of the topic you want to receive alerts for manual approval with your sns arn.

    ```cdk deploy --parameters SNSarn=<SNS arn of the topic you want to receive alerts for human approval>``` 

8. The deployment will create the following AWS resources:
   - a CodeCommmit repository with all files of [source_code](/source_code) folder which holds the source code for SCP creation and management,
   - 3 CodeBuild projects, one for each of the pipeline stages - code validation, policy checks, code deploy (as defined in the architecture diagram above)
   - a human approval stage in the pipeline 
   - a CodePipeline tying all the CodeBuild steps togather
   - necessary AWS resources to support the management of the pipeline. For details of the AWS resources created by this pipeline [refer to this readme](/SCP_Management_Pipeline/README.md)

10. Once the pipeline runs, and if the SCPs specified in the templates pass all the validation steps, a notification will be sent to the subscribed email/mobile address on the SNS topic that was provided during CDK deploy. Once you approve the changes, the pipeline will attempt to deploy SCPs in your AWS Organization if the correct organization structure exists. 

#### Cleanup

Use the following command to delete the infrastructure that was provisioned as part of the examples in this blog post.

  ```cdk destroy```

### SCPs Deployment through your chosen pipeline

For deploying the SCPs through your chosen pipeline or directly in your organization using Terraform as the Infrastructure-as-Code (IaC), navigate directly to the [source_code](/source_code) folder.

There are detail steps mentioned about the scripts defined and how to deploy them.

## Security
See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License
This library is licensed under the MIT-0 License. See the LICENSE file.
