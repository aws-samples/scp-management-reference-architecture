# SCP Import

This document explains how to automatically create IaC from manually-managed SCPs.

# Steps

0. Determine if you want to run this in the management or Organizations delegated admin account. Generally, you should use a delegated administrator when possible.
   1. If using a delegated administrator account, you will need to make sure that the Organizations service gives appropriate permissions to the account. This is an example policy to provide SCP management permissions in the Organizations Settings menu (replace XXXX with your delegated administrator account ID):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "ViewAWSOrganizationsResources",
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::XXXXXXXXXXXX:root"
         },
         "Action": [
           "organizations:DescribeOrganization",
           "organizations:DescribeOrganizationalUnit",
           "organizations:DescribeAccount",
           "organizations:DescribePolicy",
           "organizations:DescribeEffectivePolicy",
           "organizations:ListRoots",
           "organizations:ListOrganizationalUnitsForParent",
           "organizations:ListParents",
           "organizations:ListChildren",
           "organizations:ListAccounts",
           "organizations:ListAccountsForParent",
           "organizations:ListPolicies",
           "organizations:ListPoliciesForTarget",
           "organizations:ListTargetsForPolicy",
           "organizations:ListTagsForResource"
         ],
         "Resource": "*"
       },
       {
         "Sid": "DelegatingAllActionsForServiceControlPolicies",
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::XXXXXXXXXXXX:root"
         },
         "Action": [
           "organizations:CreatePolicy",
           "organizations:UpdatePolicy",
           "organizations:DeletePolicy",
           "organizations:AttachPolicy",
           "organizations:DetachPolicy",
           "organizations:EnablePolicyType",
           "organizations:DisablePolicyType"
         ],
         "Resource": [
           "arn:aws:organizations::*:policy/*/service_control_policy/*",
           "arn:aws:organizations::*:account/*/*",
           "arn:aws:organizations::*:ou/*/*",
           "arn:aws:organizations::*:root/*/*"
         ]
       }
     ]
   }
   ```
   For more details, see https://medium.com/cloud-security/delegating-scp-management-to-governance-team-via-aws-organizations-53334a31b71c
1. In the management or Organizations delegated Admin account, run the script `generate_scp_ou_structure_and_import.py`
   1. This script will generate the following content:
      1. A `service_control_policies` folder that contains a folder structure mirroring the OU structure of the Organization. Within this folder, there are two subfolders: `ROOT` and `SHARED`. Within these folders are JSON files with Service Control Policies.
      2. Two import manifest (`.tf`) files, one for SCP imports and one for SCP attachment imports.
2. Deploy the CloudFormation template `scp-pipeline.yaml` to create a pipeline that uses Terraform to manage SCPs.
   1. You may need to update the template's KMS policy to give the role creating the CloudFormation Stack admin access to the key.
   2. This template has a CodeStar resource to connect the pipeline to BitBucket. After deploying the CFT, you will need to perform some manual configuration to finish BitBucket setup (https://console.aws.amazon.com/codesuite/settings/connections)
   3. If you want to use a different source, such as CodeCommit or GitHub, you will need to modify the CFT.
   4. Deploying the CFT requires the following permissions (may require changes if you use non-default arguments):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "CreateKmsKeys",
         "Effect": "Allow",
         "Action": ["kms:CreateKey", "kms:ListAliases"],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": ["kms:CreateAlias", "kms:DeleteAlias"],
         "Resource": ["arn:aws:kms:*:*:alias/scp-*", "arn:aws:kms:*:*:key/*"]
       },
       {
         "Effect": "Allow",
         "Action": [
           "codestar-connections:CreateConnection",
           "codestar-connections:DeleteConnection"
         ],
         "Resource": "arn:aws:codestar-connections:*:*:connection/*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "codepipeline:CreatePipeline",
           "codepipeline:DeletePipeline"
         ],
         "Resource": "arn:aws:codepipeline:*:*:scp-pipeline"
       },
       {
         "Effect": "Allow",
         "Action": ["codebuild:CreateProject", "codebuild:DeleteProject"],
         "Resource": "arn:aws:codebuild:*:*:project/scp-*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "iam:CreateRole",
           "iam:UpdateRole",
           "iam:DeleteRole",
           "iam:AttachRolePolicy",
           "iam:DetachRolePolicy",
           "iam:GetRolePolicy",
           "iam:PutRolePolicy"
         ],
         "Resource": "arn:aws:iam::*:role/scp-*"
       }
     ]
   }
   ```
3. If you do not already have a Terraform state bucket and Terraform DynamoDB lock table for backending Terraform, use the `bootstrap` folder to deploy those resources.
  1. Once you have a TF state bucket, ensure that the `backend.tf` file points to your Terraform state bucket.
5. If you have not done so, update your repository to include the files generated by `generate_scp_ou_structure_and_import.py` using `git`. Make sure you include the `service_control_policies` directory, `scp_module` directory, import manifests, backend manifest, and `resolve_scp_data.py` file at a minimum.
6. Follow along with the pipeline execution, fix any errors, and manually approve the changes if the `terraform plan` looks accurate.
7. After the first successful `apply` of the pipeline, you may remove the `import` files or rename them (eg. to `.tf.bak`) for historical reference. This will require updating the CFT template and deploying it via CloudFormation.
8. Make changes to SCPs using this module (see instructions for managing below) and don't make any more changes using the console!
   1. For inspiration on SCPs to apply to your environment, check out: https://aws-samples.github.io/aws-iam-permissions-guardrails/guardrails/scp-guardrails.html

# Managing this repository

When making changes, you can either update human-readable information in `List-of-SCPs.md` or add in-line comments to the `scp_define_attach.tf` file. It is generally advisable to include some explanation of what statements do or what change tickets they are associated with.

## Adding new SCPs

1. To add a new SCP, you will need to create a JSON file in the appropriate location, with a `policy` key containing the policy and a `description` key containing a description of the policy. If the SCP is used in just one OU or account, create the JSON file in the folder for that OU/account. If the SCP is used in multiple locations, create it in the `service_control_policies/SHARED` folder and create placeholder files (eg. `security_baseline.placeholder.shared`) in each location where it will be attached (short justification: placeholders help avoid exceeding the SCP-OU attachment limit of 5).

## Modifying existing SCPs

1. Modify the JSON file. You can add, remove, or edit statements and the pipeline will update them in place.
2. If you are applying a single-use SCP to another OU/Account, you will need to move the policy to the `SHARED` directory and make references to it using a `.shared` file.

## Removing/Detaching SCPs

1. To detach an SCP, simply delete the JSON file.
2. If all attachments of an SCP are removed, the SCP itself will also be removed. SCPs can be stored in the code repository `SHARED` folder but will not be created without an attachment.

## Handling OU restructures

1. Re-run the `generate_scp_ou_structure_and_import.py` script and modify as necessary to align SCPs to the new structure.
