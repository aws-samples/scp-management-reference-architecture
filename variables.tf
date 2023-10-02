#################################################
# Define Variables to pass list of OUs or Account IDs to which SCPs need to be attached.data ""\\ "name" {
# This is applicable only if you want to attach your SCP to multiple OUs but not all
# Values for the below mentioned variables should be provided in the terraform.tfvars file in the same directory as the current file is
################################################

variable "apply_allowed_services_ou_ids" {
  type        = list(string)
  description = "List of OUs to which Account_Baseline_MultiOU SCP will be attached to prevent using services outside allowed list"
}

variable "apply_immutable_vpc_ou_ids" {
  type        = list(string)
  description = "List of OUs to which Network_Baseline_MultiOU SCP will be attached to prevent VPC boundary privilege actions"
}

variable "infrastructure_id" {
  type        = string
  description = "ID of the Production Infrastructure OU"
}

variable "root_id" {
  type        = string
  description = "ID of the Organization Root"
}