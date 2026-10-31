variable "region" {
  type        = string
  description = "AWS region for the example deployment"
  default     = "eu-west-1"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}

variable "allowed_cidr_blocks" {
  type        = list(string)
  description = "CIDR blocks allowed to reach the application security group"
  default     = []
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR range for the example VPC"
  default     = "10.40.0.0/16"
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "Two private subnet CIDRs used by the application and database"
  default     = ["10.40.1.0/24", "10.40.2.0/24"]
  validation {
    condition     = length(var.private_subnet_cidrs) == 2
    error_message = "Exactly two private subnet CIDRs are required."
  }
}

variable "eks_oidc_issuer_url" {
  type        = string
  description = "Issuer URL from the EKS cluster OIDC provider"
}

variable "eks_oidc_thumbprint" {
  type        = string
  description = "Trusted root CA thumbprint for the EKS OIDC issuer"
  validation {
    condition     = can(regex("^[A-Fa-f0-9]{40}$", var.eks_oidc_thumbprint))
    error_message = "The OIDC thumbprint must be 40 hexadecimal characters."
  }
}
