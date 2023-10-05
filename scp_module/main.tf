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
  for_each = toset(var.scp_target_list)
  policy_id = aws_organizations_policy.create_scp.id
  target_id = each.key
}