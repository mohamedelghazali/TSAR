variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "aws_account_id" {
  type = string
}

variable "gcp_project" {
  type = string
}

variable "gcp_region" {
  type    = string
  default = "europe-west1"
}

variable "azure_subscription_id" {
  type = string
}

variable "azure_tenant_id" {
  type = string
}

variable "gcp_workload_identity_subject" {
  type = string
}

variable "azure_workload_identity_subject" {
  type = string
}

variable "aws_cross_cloud_subject" {
  type = string
}

variable "eks_oidc_id" {
  type = string
}
