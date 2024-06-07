{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PreventDefaultClassicVPCSubnet",
            "Effect": "Deny",
            "Action": [
                "ec2:CreateDefaultSubnet",
                "ec2:CreateDefaultVpc",
                "ec2:RestoreAddressToClassic",
                "ec2:AttachClassicLinkVpc",
                "ec2:EnableVpcClassicLink",
                "ec2:EnableVpcClassicLinkDnsSupport"
            ],
            "Resource": "*"
        },
        {
            "Sid": "RequireImdsV2",
            "Effect": "Deny",
            "Action": ["ec2:RunInstances"],
            "Resource": "arn:aws:ec2:*:*:instance/*",
            "Condition": {
                "NumericGreaterThan": {
                    "ec2:MetadataHttpPutResponseHopLimit": "1"
                }
            }
        },
        {
            "Sid": "PreventIMDSv2Removal",
            "Effect": "Deny",
            "Action": ["ec2:ModifyInstanceMetadataOptions"],
            "Resource": "arn:aws:ec2:*:*:instance/*",
            "Condition": {
                "StringEquals": {
                    "ec2:MetadataHttpTokens": "required"
                }
            }
        },
        {
            "Sid": "PreventVPCActionsinAllOUswithWhitelist",
            "Effect": "Deny",
            "Action": [
                "ec2:CreateVpc",
                "ec2:DeleteVpc",
                "ec2:AssociateVpcCidrBlock",
                "ec2:DisassociateVpcCidrBlock",
                "ec2:ModifyVpcAttribute",
                "ec2:MoveAddressToVpc",
                "ec2:ModifyVpcTenancy",
                "ec2:CreateFlowLogs",
                "ec2:DeleteFlowLogs"
            ],
            "Resource": "*",
            "Condition": {
                "ArnNotLike": {
                    "aws:PrincipalARN": [
                        "arn:aws:iam::${master_account_id}:role/AWSAFTService",
                        "arn:aws:iam::*:role/AWSControlTowerExecution",
                        "arn:aws:iam::*:role/AWSAFTExecution",
                        "arn:aws:iam::*:role/<ALL PIPELINE ROLES PLACEHOLDER>",
                        "arn:aws:iam::*:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_<PERMISSION SET NAME>_*"
                    ]
                }
            }
        },
        {
            "Sid": "PreventMLmodelsnonVPCcreation",
            "Effect": "Deny",
            "Action": [
                "sagemaker:CreateHyperParameterTuningJob",
                "sagemaker:CreateModel",
                "sagemaker:CreateNotebookInstance",
                "sagemaker:CreateTrainingJob"
            ],
            "Resource": "arn:aws:ec2:*:*:instance/*",
            "Condition": {
                "Null": {
                    "sagemaker:VpcSubnets": "true"
                }
            }
        }
    ]
}
