########################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
########################################################################

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.4.0"
    }
  }
}

provider "aws" {
    region = "us-east-1"
}