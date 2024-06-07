{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PreventRootActivities",
            "Effect": "Deny",
            "Action": ["*"],
            "Resource": "*",
            "Condition": {
                "ArnLike": {
                    "aws:PrincipalARN": ["arn:aws:iam::*:root"]
                }
            }
        },
        {
            "Sid": "PreventKMSKeyDelete",
            "Effect": "Deny",
            "Action": ["kms:ScheduleKeyDeletion"],
            "Resource": "*",
            "Condition": {
                "ArnNotLike": {
                    "aws:PrincipalARN": [
                        "arn:aws:iam::${master_account_id}:role/AWSAFTService",
                        "arn:aws:iam::*:role/AWSControlTowerExecution",
                        "arn:aws:iam::*:role/AWSAFTExecution",
                        "arn:aws:iam::*:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_<PERMISSION SET NAME>_*",
                        "arn:aws:iam::*:role/<ALL PIPELINE ROLES PLACEHOLDER>"
                    ]
                }
            }
        },
        {
            "Sid": "RestrictIAMUserCreation",
            "Effect": "Deny",
            "Action": [
                "iam:AttachUserPolicy",
                "iam:CreateUser",
                "iam:PutUserPolicy"
            ],
            "Resource": "*",
            "Condition": {
                "ArnNotLike": {
                    "aws:PrincipalARN": [
                        "arn:aws:iam::${master_account_id}:role/AWSAFTService",
                        "arn:aws:iam::*:role/AWSControlTowerExecution",
                        "arn:aws:iam::*:role/AWSAFTExecution",
                        "arn:aws:iam::*:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_<PERMISSION SET NAME>_*",
                        "arn:aws:iam::*:role/<ALL PIPELINE ROLES PLACEHOLDER>"
                    ]
                }
            }
        },
        {
            "Sid": "RestrictIAMUserAccessKeysPasswords",
            "Effect": "Deny",
            "Action": [
                "iam:CreateAccessKey",
                "iam:CreateLoginProfile"
            ],
            "Resource": "*",
            "Condition": {
                "ArnNotLike": {
                    "aws:PrincipalARN": [
                        "arn:aws:iam::*:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_<PERMISSION SET NAME>_*",
                        "arn:aws:iam::*:role/<ALL PIPELINE ROLES PLACEHOLDER>"
                    ]
                }
            }
        },
        {
            "Sid": "PreventIAMFederationActions",
            "Effect": "Deny",
            "Action": [
                "iam:CreateSAMLProvider",
                "iam:DeleteSAMLProvider"
            ],
            "Resource": "*"
        },
        {
            "Sid": "PreventPrivilegeIAMRoleActions",
            "Effect": "Deny",
            "Action": [
                "iam:AttachRolePolicy",
                "iam:DeleteRole*",
                "iam:PutRolePermissionsBoundary",
                "iam:PutRolePolicy",
                "iam:UpdateAssumeRolePolicy",
                "iam:UpdateRole*"
            ],
            "Resource": [
                "arn:aws:iam::*:role/<BREAKGLASS ROLES>",
                "arn:aws:iam::*:role/<PRIVILEGED ROLES>"
            ],
            "Condition": {
                "ArnNotLike": {
                    "aws:PrincipalARN": [
                        "arn:aws:iam::${master_account_id}:role/AWSAFTService",
                        "arn:aws:iam::*:role/AWSControlTowerExecution",
                        "arn:aws:iam::*:role/AWSAFTExecution",
                        "arn:aws:iam::*:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_<PERMISSION SET NAME>_*",
                        "arn:aws:iam::*:role/<ALL PIPELINE ROLES PLACEHOLDER>"
                    ]
                }
            }
        },
        {
            "Sid": "PreventSecurityServiceModifications",
            "Effect": "Deny",
            "Action": [
                "guardduty:CreatePublishingDestination",
                "guardduty:StopMonitoringMembers",
                "guardduty:TagResource",
                "guardduty:UntagResource",
                "guardduty:Update*",
                "guardduty:Delete*",
                "guardduty:Disassociate*",
                "securityhub:Delete*",
                "securityhub:BatchDisableStandards",
                "securityhub:TagResource",
                "securityhub:UntagResource",
                "securityhub:Update*",
                "securityhub:DisableSecurityHub",
                "securityhub:Disassociate*",
                "access-analyzer:DeleteAnalyzer",
                "cloudtrail:StopLogging",
                "cloudtrail:DeleteTrail",
                "cloudtrail:PutEventSelectors",
                "cloudtrail:RemoveTags",
                "cloudtrail:UpdateTrail",
                "config:Delete*",
                "config:StopConfigurationRecorder",
                "config:PutDeliveryChannel"
            ],
            "Resource": "*",
            "Condition": {
                "ArnNotLike": {
                    "aws:PrincipalARN": [
                        "arn:aws:iam::${master_account_id}:role/AWSAFTService",
                        "arn:aws:iam::*:role/AWSControlTowerExecution",
                        "arn:aws:iam::*:role/AWSAFTExecution",
                        "arn:aws:iam::*:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_<PERMISSION SET NAME>_*",
                        "arn:aws:iam::*:role/<ALL PIPELINE ROLES PLACEHOLDER>"
                    ]
                }
            }
        },
        {
            "Sid": "EnforceGenAIAccessedDataEncrypt",
            "Effect": "Deny",
            "Action": [
                "bedrock:*",
                "qbusiness:*",
                "q:*"
            ],
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        }
    ]
}
