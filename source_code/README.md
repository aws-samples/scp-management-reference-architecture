# Service Control Policy (SCP) Deployment Code

This repo contains the AWS Service Control Policies (SCPs) custom built for your company's AWS organiztion, and attaches policies to specific AWS Organizational Units. **This DOES NOT include the SCPs created by AWS Control Tower as Control tower Guardrails**

## Content

- [Code Walk-through](#code-walk-through)
  - [Directory Structure](#directory-structure)
  - [Scripts in this Directory](#scripts-in-this-directory)
  - [Sub-Directories](#sub-directories)
    - [service\_control\_policies](#service_control_policies) 
    - [scp\_module](#scp_module)
  - [SCP File Naming Convention](#scp-file-naming-convention)
    - [SCP File Names for Root:](#scp-file-names-for-root)
    - [SCP File Names for Multiple OUs:](#scp-file-names-for-multiple-ous)
    - [SCP File Names for any specific OU:](#scp-file-names-for-any-specific-ou)
    - [SCP File Names for any specific AWS Account:](#scp-file-names-for-any-specific-aws-account)
- [How to Deploy](#how-to-deploy)
    - [Prerequisites to deploy through CLI](#prerequisites-to-deploy-through-cli)
    - [Code edits required before deployment](#code-edits-required-before-deployment)
    - [Steps to deploy SCP code via terraform](#steps-to-deploy-scp-code-via-terraform)
- [Steps to manage SCPs](#steps-to-manage-scps)
  - [Steps to follow for Adding New SCPs](#steps-to-follow-for-adding-new-scps)
  - [Steps to edit existing SCPs](#steps-to-edit-existing-scps)
  - [Steps to follow for Denying All Actions from a specific OU](#steps-to-follow-for-denying-all-actions-from-a-specific-ou)

# Code Walk-through

## Directory Structure

```sh
.
├── scp_define_attach.tf # <-- the main code that defines the SCPs to be created along with its necessary configurations for creation in an AWS organization environment.
├── variables.tf         # <-- variable definition file
├── terraform.tfvars     # <-- pass values to variables before execution through this file
├── providers.tf         # <-- defines which Terraform plugin to use and how to authenticate with the cloud provider (in this case - AWS)
├── backend.tf           # <-- defines where the state file of the current infrastructure will be stored
├── service_control_policies # <-- a directory with sub-directories specific to the OUs to which SCPs are directly attached
    ├── Root                 # <-- all SCP policies to be attached directly to Root
    ├── InfrastructureOU     # <-- all SCP policies to be attached directly to Infrastructure OU
    ├── MultiOUs             # <-- all SCP policies to be attached directly to the list of multiple OUs.
├── scp_module          # <-- code for creating an SCP and attaching it to defined targets
├── find_blocking_scps  # <-- code to identify which existing SCPs are denying your actions 
├── List-of-SCPs.md     # <-- A file containing overview of all the SCPs enabled through this repository.      
└── README.md           # <-- This file
```

## Scripts in this Directory

1. **_`scp_define_attach.tf`_** - this is the main terraform file that is executed. All the SCPs creation and attachement calls are made from this file.
2. **_`variables.tf`_** - this is where you define all the runtime variables that you want to pass to the SCP creaion / updation process, which includes account IDs, OU names etc.
3. **_`terraform.tfvars`_** - this is the file where you provide the runtime value for each of the variables defined in `variables.tf` file
4. **_`providers.tf`_** - this is to declare all the providers that Terraform need to interact with, like cloud providers, SaaS providers, and other APIs
5. **_`backend.tf`_** - this is to define where in your AWS environment Terraform should store its state data files.

> NOTE: It is recommended to store state files in an Amazon S3 bucket which provides a durable and scalable storage solution. Storing on Amazon S3 also enables collaboration that allows you to share state file with others. In addition to using an Amazon S3 bucket for managing the files, you can use an Amazon DynamoDB table to lock the state file. This will allow only one person to modify a particular state file at any given time. It will help to avoid conflicts and enable safe concurrent access to the state file. There are other options available as well such as remote backend on terraform cloud and third party backends. Ultimately, the best method for managing terraform state files on AWS will depend on your specific requirements.

## Sub-Directories

### service_control_policies

- this Directory contains all the custom SCP policy statements built for your company, categorized based on the Orgaization Unit (OU) to which there are attached. For example, in this directory all the SCP policy files you will see under the `Root` sub-directory are attached directly to the Root OU.
- **scripts in this directory:** All SCP policy files are defined as `.tpl` files. Files with `.tpl` extensions are template files that gives you the privilege to pass user-defined variables at runtime to the file.
- In this directory all the `.tpl` files are in json format

### scp_module

- this Directory contains the terraform resources for
  1. creating a SCP in the organization's management account
  2. attaching the above created SCP to a desired target OU or AWS Account as provided by you.
     > NOTE: Benefit of this module directory is defining the SCP creation and attachment resources only once in your repository and call these two resources as many times as required in a modularized approach. Thus maintainig standardized coding and avoid repeated resource definition in code.
- **scripts in this directory:**
  1. **_`main.tf`_** - this is the terraform file where two resources are defined.
     - `resource "aws_organizations_policy"` for creating a SCP
     - `resource "aws_organizations_policy_attachment"` for attaching a SCP. This block is optional and depends on whether you want to attach a SCP to a target. Decision of this resource execution varies on the runtime input value passed to `main.tf` via the `scp_target_list` variable. If you do not pass any value for this variable, this resource block will not be executed
  2. **_`variables.tf`_** - this is where you define all the values that are passed to the `main.tf` file.

## SCP File Naming Convention

> NOTE:
>
> 1. All SCP files created in this repository are template files (`.tpl` extension)
> 2. Any SCP file you create in this repository should have a suffix of `.json` followed by the extension `.tpl`

### SCP File Names for Root:

- Account_Baseline_Root.json.tpl
- Security_Baseline_Root.json.tpl
- Infrastructure_Baseline_Root.json.tpl
- Data_Baseline_Root.json.tpl

### SCP File Names for Multiple OUs:

- Account_Baseline_*Logical Keyword*.json.tpl
- Security_Baseline_*Logical Keyword*.json.tpl
- Infrastructure_Baseline_*Logical Keyword*.json.tpl
- Data_Baseline_*Logical Keyword*.json.tpl
  > This logical keyword should define the logical grouping of multiple OUs you have planned for applying the SCP statements. **For example**, if you have a set of VPC and EC2 restrictions that you want to put on all non-infrastructure OUs then your SCP file name can be `Infrastructure_Baseline_NonInfraOUs.json.tpl`

### SCP File Names for any specific OU:

- Account*Baseline*_OU Name_.json.tpl
- Security*Baseline*_OU Name_.json.tpl
- Infrastructure*Baseline*_OU Name_.json.tpl
- Data*Baseline*_OU Name_.json.tpl

### SCP File Names for any specific AWS Account:

- Account*Baseline*_Account Name or ID_.json.tpl
- Security*Baseline*_Account Name or ID_.json.tpl
- Infrastructure*Baseline*_Account Name or ID_.json.tpl
- Data*Baseline*_Account Name or ID_.json.tpl

# How to Deploy
You can directly deploy this code in your AWS organizations through the CLI using terraform or you can download this code into your choice of CI/CD pipeline.

## Prerequisites to deploy through CLI
- [AWS CLI configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) in your local environment
- [Terraform installed](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) in your local environment
- [Access configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) to the AWS organization's management account where SCPs will be deployed.

## Code edits required before deployment

1. The [terraform.tfvars](terraform.tfvars) file contains the value for all the SCP targets to which the SCPs are planned to be attached. Before deploying the code replace the value of each SCP target variable with the appropriate values of your AWS organization. 
2. The [backend.tf](backend.tf) file contains the value of the S3 bucket and DynamboDB table used for storing and locking the Terraform state files respectively. Provide the name (not ARN) of these two AWS resources that will be used by terraform.

## Steps to deploy SCP code via terraform

Run the following commands from this current directory

1. Use the following command to initialize the working directory containing Terraform configuration files.

    ```terraform init```
    
2. On the success of the previous command use the following command to validate the configuration files in this terraform initialized directory.

    ```terraform validate```

3. Next use the following command to create an execution plan, which lets you preview the changes that Terraform plans to make to your infrastructure.

    ```terraform plan```

4. As you approve the plan, use the following command to execute the actions proposed in a Terraform plan.

    ```terraform apply -auto-approve```

# Steps to manage SCPs

## Steps to follow for Adding New SCPs

1.  First identify the target to which your new SCP statement should be attached.
    - **If you want to attach your SCP policy actions to all OUs**, check the `Root` sub-directory in `service_control_policies` directory
    - **If you want to attach your SCP policy actions to Multiple OUs but not All**, check the `MultiOUs` sub-directory in `service_control_policies` directory
    - **If you want to attach your SCP policy actions to a specific OU or AWS Account**, check under `service_control_policies` directory if a sub-directory exist with a name same as the OU or AWS Account name you want to attach your policy actions.
      - If you find one, then go to the next step to see how to add the policy actions
      - If you DONT find the appropriate sub-directory then create one with a name exactly same as the OU or AWS Account name you want to attach your policy actions, then go to next step.
2.  Based on the target chosen for your SCP navigate to the appropriate sub-directory, next identify under what category does your new SCP policy actions belong out of the below mentioned four catgeories.
    - `account_baseline_scp` - choose this category if yor policy actions are specific to governance or account management services
    - `security_iam_baseline_scp` - choose this category if yor policy actions are specific to security services
    - `infrastructure_baseline_scp` - choose this category if yor policy actions are specific to network services
    - `data_logging_baseline_scp` - choose this category if yor policy actions are specific to storage services
3.  Next, check if an SCP file with a name similar to your above chosen SCP category exist in the sub-directory you have decided as your SCP target.
    - If you find an existing file with a name similar to your above chosen SCP category then edit the identified SCP file, either add your actions to an existing statement or create a new statement in the policy file based on the SCP policy size limit and your requirements. Go to Step 4.
    - If you DONT find an existing file with a name similar to your above chosen SCP category then create a new SCP policy file with your policy actions. The name of this new SCP file must follow the standard naming convention defined in [SCP File Naming Convention](#scp-file-naming-convention)
      - If you created a new SCP file then creating the policy file, next you have to create a module block in the `scp_define_attach.tf` file to create a SCP policy and attach it to the target.
      - In the new module block, you will have to provide the following parameters:
        - source = `"../scp_module"` - this source path should not be changed
        - scp*name = \_a name that follows the SCP naming standards as outlined in this README*
        - scp*desc = \_a short description about the SCP*
        - scp*policy = jsonencode(jsondecode(templatefile("../service_control_policies/\_path of .tpl file*", { _variables to pass to the policy file_})))
        - scp_target_list = [*either a target OU or Account ID or a series of OUs. In any case this should be passed as a list even if the target is just one ID*]
4.  Update the `List-of-SCPs.md` with details of the new SCP policy file added to the service_control_policies directory.
5.  Next, push your code for a PR and after approval the new SCP policy actions will be reflected in your AWS organizations.

> NOTE:
>
> 1. If you want to pass any specific value to the SCP policy like account ID or a role name etc, you can pass it as an input variable to the `scp_policy`
> 2. If you want to attach the SCP to a list of OUs and no other SCPs are already attached to this target list of OUs, then you can define a variable in the `variables.tf` as a list(string). Define the value of this variable in the `terraform.tfvars` file and enter the name of all of your chosen OUs in it.

## Steps to edit existing SCPs

Either edit policy's Action or Resource or Conditions

1.  First identify where in `service_control_policies` directory the SCP policy is defined
2.  Based on the correct `.tpl file` chosen, next edit the file.
3.  Update the `List-of-SCPs.md` with details of the new policy statement added to an existing SCP in service_control_policies directory.
4.  After file edit, push your code for a PR and after approval the policy changes will be reflected in your AWS organizations.

## Steps to follow for Denying All Actions from a specific OU

Remove the `FullAWSAccess` policy that is directly attached to the OU to which you want to deny all actions.

> NOTE: The `FullAWSAccess` policy inherited from a parent OU will not allow permissions to a principal (OU or account) until you directly attach the `FullAWSAccess` policy to the principal.
