terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      ManagedBy   = "terraform"
      Environment = var.environment
      Project     = "tsar-example"
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}
