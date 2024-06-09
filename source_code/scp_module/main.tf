################################################################
# Creating an SCP and then attaching it to a Target OU / Account
################################################################

# Resource to create an SCP in the Management Account
resource "aws_organizations_policy" "create_scp" {
  name        = var.scp_name
  description = var.scp_desc
  type        = "SERVICE_CONTROL_POLICY"
  content     = var.scp_policy
}

# Resource to attach the above created SCP to a specifc Target (that can be Root OU or any individual OU or AWS Account)
resource "aws_organizations_policy_attachment" "attach_scp" {
  count     = length(var.scp_target_list) != 0 ? length(var.scp_target_list) : 0 # check if an SCP target is passed from the calling module then only this resource block will be executed
  policy_id = aws_organizations_policy.create_scp.id
  target_id = var.scp_target_list[count.index]
}