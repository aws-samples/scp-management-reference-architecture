{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DenyPrivilegeVPCEC2Actions",
            "Effect": "Deny",
            "Action": [
                "ec2:AssociateDhcpOptions",
                "ec2:CreateDhcpOptions",
                "ec2:DeleteDhcpOptions",
                "ec2:AssociateSubnetCidrBlock",
                "ec2:DisassociateSubnetCidrBlock",
                "ec2:CreateSubnet",
                "ec2:DeleteSubnet",
                "ec2:ModifySubnetAttribute",
                "ec2:CreateNetworkAcl",
                "ec2:DeleteNetworkAcl",
                "ec2:CreateNetworkAclEntry",
                "ec2:DeleteNetworkAclEntry",
                "ec2:CreateRoute",
                "ec2:DeleteRoute",
                "ec2:ReplaceRoute",
                "ec2:AssociateRouteTable",
                "ec2:CreateRouteTable",
                "ec2:DeleteRouteTable",
                "ec2:DisassociateRouteTable",
                "ec2:ReplaceRouteTableAssociation"
            ],
            "Resource": "*",
            "Condition": {
                "ArnNotLike": {
                    "aws:PrincipalARN": [
                        "arn:aws:iam::${master_account_id}:role/AWSAFTService",
                        "arn:aws:iam::*:role/AWSControlTowerExecution",
                        "arn:aws:iam::*:role/AWSAFTExecution",
                        "arn:aws:iam::*:role/aws-reserved/sso.amazonaws.com/us-west-2/AWSReservedSSO_PermissionSetName_*",
                        "arn:aws:iam::*:role/ALL PIPELINE ROLES PLACEHOLDER"
                    ]
                }
            }
        }
    ]
}
