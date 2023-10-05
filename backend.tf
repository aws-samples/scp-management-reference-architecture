# Variable use is not allowed, must be hard-coded to the account you want to apply to
terraform {
  backend "s3" {
    encrypt        = "true"
    bucket         = "iam-identitycenter-YOUR ACCOUNT ID-tf-state"
    dynamodb_table = "tf-state-lock"
    key            = "scp.tfstate"
    region         = "us-east-2" # UPDATE REGION IF YOU DON'T LOVE OHIO
    profile        = "YOUR ACCOUNT ID"
  }
}
