terraform {
  backend "s3" {
    bucket         = "" # name (not ARN) of the S3 bucket where you want to store all the state files of terraform
    key            = "terraform.tfstate" #the key name should not be replaced
    region         = "us-east-1" #your choice of AWS region where the S3 bucket is defined
    dynamodb_table = "" # name (not ARN) of the DynamoDB table used to lock the each state file
    encrypt        = true
  }
}

## NOTE: If the chosen S3 bucket and DynamoDB table are in different AWS accounts than where you deploy the SCPs, then make sure thwe IAM role you use for execution have the necessary cross-account access to the S3 bucket and dynamoDB table.