# Data block to get information about the organization that the user's account belongs to
data "aws_organizations_organization" "ou_model" {
}

#data "terraform_remote_state" "ou_model" {
#  backend = "s3"
#  config = {
#    bucket = "" #S3 Bucket Name where the remote state files for the Organization building terraform code is stored
#    key    = "" #exact location in the bucket
#    region = "" #AWS region where AWS organizations is enabled
#  }
#}

#####################
## Root Level SCPs
#####################
module "account_baseline_root_scp" {
  source          = "./scp_module"
  scp_name        = "Account_Baseline_Root"
  scp_desc        = "This SCP has policy statements to restrict account baselining and compliance actions in your AWS Org at Root level."
  scp_policy      = jsonencode(jsondecode(templatefile("./service_control_policies/Root/Account_Baseline_Root.json.tpl", { master_account_id = data.aws_organizations_organization.ou_model.master_account_id })))
  scp_target_list = [var.root_id]
}

module "network_baseline_root_scp" {
  source          = "./scp_module"
  scp_name        = "Network_Baseline_Root"
  scp_desc        = "This SCP has policy statements to restrict network baselining actions in your AWS Org at Root level."
  scp_policy      = jsonencode(jsondecode(templatefile("./service_control_policies/Root/Network_Baseline_Root.json.tpl", { master_account_id = data.aws_organizations_organization.ou_model.master_account_id })))
  scp_target_list = [var.root_id]
}

module "security_baseline_root_scp" {
  source          = "./scp_module"
  scp_name        = "Security_Baseline_Root"
  scp_desc        = "This SCP has policy statements to restrict security baselining actions in your AWS Org at Root level."
  scp_policy      = jsonencode(jsondecode(templatefile("./service_control_policies/Root/Security_Baseline_Root.json.tpl", { master_account_id = data.aws_organizations_organization.ou_model.master_account_id })))
  scp_target_list = [var.root_id]
}

module "storage_baseline_root_scp" {
  source          = "./scp_module"
  scp_name        = "Storage_Baseline_Root"
  scp_desc        = "This SCP has policy statements to restrict storage baselining actions in your AWS Org at Root level."
  scp_policy      = jsonencode(jsondecode(templatefile("./service_control_policies/Root/Storage_Baseline_Root.json.tpl", { master_account_id = data.aws_organizations_organization.ou_model.master_account_id })))
  scp_target_list = [var.root_id]
}

#####################
## Multi OU SCPs
#####################
module "account_baseline_allowedservices_scp" {
  source          = "./scp_module"
  scp_name        = "Account_Baseline_AllowedServices"
  scp_desc        = "This SCP has policy statements to restrict account baselining actions in multiple OUs of your AWS Org."
  scp_policy      = jsonencode(jsondecode(templatefile("./service_control_policies/MultiOUs/Account_Baseline_AllowedServices.json.tpl", { master_account_id = data.aws_organizations_organization.ou_model.master_account_id })))
  scp_target_list = var.apply_allowed_services_ou_ids
}

module "network_baseline_vpcboundaries_scp" {
  source          = "./scp_module"
  scp_name        = "Network_Baseline_VPCBoundaries"
  scp_desc        = "This SCP has policy statements to restrict VPC and EC2 baselining actions in multiple OUs of your AWS Org."
  scp_policy      = jsonencode(jsondecode(templatefile("./service_control_policies/MultiOUs/Network_Baseline_VPCBoundaries.json.tpl", { master_account_id = data.aws_organizations_organization.ou_model.master_account_id })))
  scp_target_list = var.apply_immutable_vpc_ou_ids
}

##########################
## Infrastructure OU SCPs
##########################
module "network_baseline_infraOU_scp" {
  source          = "./scp_module"
  scp_name        = "Network_Baseline_ProdInfrastructureOU"
  scp_desc        = "This SCP has policy statements to restrict privilege VPC and EC2 baselining actions only in Infrastructure OU of your AWS Org."
  scp_policy      = jsonencode(jsondecode(templatefile("./service_control_policies/Production_Infrastructure/Network_Baseline_InfrastructureOU.json.tpl", { master_account_id = data.aws_organizations_organization.ou_model.master_account_id })))
  scp_target_list = [var.production_infrastructure_id]
}

##############################################################################
## Outputs (for SCP length validation) for All SCPs attached to the Root
##############################################################################
output "account_baseline_root_scp_byte_length" {
  value = module.account_baseline_root_scp.scp_byte_size
}

output "network_baseline_root_scp_byte_length" {
  value = module.network_baseline_root_scp.scp_byte_size
}

output "security_baseline_root_scp_byte_length" {
  value = module.security_baseline_root_scp.scp_byte_size
}

output "storage_baseline_root_scp_byte_length" {
  value = module.storage_baseline_root_scp.scp_byte_size
}

output "account_baseline_allowedservices_scp_byte_length" {
  value = module.account_baseline_allowedservices_scp.scp_byte_size
}

output "network_baseline_vpcboundaries_scp_byte_length" {
  value = module.network_baseline_vpcboundaries_scp.scp_byte_size
}

output "network_baseline_infraOU_scp_byte_length" {
  value = module.module.network_baseline_infraOU_scp.scp_byte_size
}
