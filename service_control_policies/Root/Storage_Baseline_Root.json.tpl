{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PreventCriticalBucketDelete",
            "Effect": "Deny",
            "Action": [
                "s3:DeleteBucket",
                "s3:DeleteBucketPolicy",
                "s3:DeleteObject",
                "s3:DeleteObjectVersion",
                "s3:DeleteObjectTagging",
                "s3:DeleteObjectVersionTagging"
            ],
            "Resource": [
                "arn:aws:s3:::PLACEHOLDER",
                "arn:aws:s3:::PLACEHOLDER/*"
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
            "Sid": "PreventS3PublicAccess",
            "Effect": "Deny",
            "Action": ["s3:PutAccountPublicAccessBlock"],
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
            "Sid": "PreventDisablingEBSEncryption",
            "Effect": "Deny",
            "Action": [
                "ec2:DisableEbsEncryptionByDefault"
            ],
            "Resource": "*"
        },
        {
            "Sid": "PreventUnencryptedRDSCreation",
            "Effect": "Deny",
            "Action": [
                "rds:CreateDBInstance",
                "rds:CreateDBCluster"
            ],
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "rds:StorageEncrypted": "false"
                }
            }
        }
    ]
}
