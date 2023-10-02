{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PreventOrgLeaveDelMod",
            "Effect": "Deny",
            "Action": [
                "organizations:LeaveOrganization",
                "organizations:DeleteOrganization"
            ],
            "Resource": "*"
        },
        {
            "Sid": "PreventSpecificLambdaChanges",
            "Effect": "Deny",
            "Action": [
                "lambda:AddPermission",
                "lambda:CreateEventSourceMapping",
                "lambda:DeleteEventSourceMapping",
                "lambda:DeleteFunction*",
                "lambda:RemovePermission",
                "lambda:UpdateEventSourceMapping",
                "lambda:UpdateFunction*"
            ],
            "Resource": "arn:aws:lambda:*:*:function:FUNCTION_NAMEPREFIX*",
             "Condition": {
                "ArnNotLike": {
                    "aws:PrincipalARN": [
                        "arn:aws:iam::${master_account_id}:role/AWSAFTService",
                        "arn:aws:iam::*:role/AWSControlTowerExecution",
                        "arn:aws:iam::*:role/AWSAFTExecution",
                        "arn:aws:iam::*:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_<PERMISSION SET NAME>_*",
                        "arn:aws:iam::*:role/ALL PIPELINE ROLES PLACEHOLDER"
                    ]
                }
            }
        },
        {
            "Sid": "PreventRegionAddOrDelete",
            "Effect": "Deny",
            "Action": [
                "account:EnableRegion",
                "account:DisableRegion"
            ],
            "Resource": "*",
            "Condition": {
                "ArnNotLike": {
                    "aws:PrincipalARN": [
                        "arn:aws:iam::${master_account_id}:role/AWSAFTService",
                        "arn:aws:iam::*:role/AWSControlTowerExecution",
                        "arn:aws:iam::*:role/AWSAFTExecution",
                        "arn:aws:iam::*:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_<PERMISSION SET NAME>_*"
                    ]
                }
            }
        },
        {
            "Sid": "PreventBillingModify",
            "Effect": "Deny",
            "Action": [
                "aws_portal:ModifyAccount",
                "aws_portal:ModifyBilling",
                "aws_portal:ModifyPaymentMethods"
            ],
            "Resource": "*"
        },
        {
            "Sid": "PreventTagModification",
            "Effect": "Deny",
            "Action": [
                "iam:UntagRole",
                "iam:UntagInstanceProfile"
            ],
            "Resource": "*",
            "Condition": {
                "ForAnyValue:StringEquals": {
                    "aws:TagKeys": ["PLACE HOLDER"]
                }
            }
        }
    ]
}
