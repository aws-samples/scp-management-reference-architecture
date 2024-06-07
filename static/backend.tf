terraform {
  backend "s3" {
    bucket         = "reinforce24-iam343-tfstate-backend"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "reinforce-iam343-tfstate-lock"
    encrypt        = true
  }
}