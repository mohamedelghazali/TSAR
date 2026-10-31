terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.40" }
    google = { source = "hashicorp/google", version = "~> 5.20" }
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.90" }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

# AWS role trust: OIDC federation from Google and Azure.
resource "aws_iam_openid_connect_provider" "google" {
  url             = "https://accounts.google.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["08745487e891c19e3078c1f2a07e452950ef36f6"]
}

resource "aws_iam_openid_connect_provider" "azure" {
  url             = "https://sts.windows.net/${var.azure_tenant_id}/"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["626d44e7d9d4e6bcb9e3f4dd4e2c1e2b6e5c5e12"]
}

data "aws_iam_policy_document" "cross_cloud_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.google.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "accounts.google.com:sub"
      values   = [var.gcp_workload_identity_subject]
    }
  }
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.azure.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "sts.windows.net/${var.azure_tenant_id}/:sub"
      values   = [var.azure_workload_identity_subject]
    }
  }
}

resource "aws_iam_role" "cross_cloud_reader" {
  name               = "tsar-cross-cloud-reader"
  assume_role_policy = data.aws_iam_policy_document.cross_cloud_assume.json
  max_session_duration = 3600
}

# GCP workload identity pool for AWS and Azure.
resource "google_iam_workload_identity_pool" "cross_cloud" {
  workload_identity_pool_id = "tsar-cross-cloud"
  display_name              = "TSAR Cross-Cloud"
}

resource "google_iam_workload_identity_pool_provider" "aws" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.cross_cloud.workload_identity_pool_id
  workload_identity_pool_provider_id = "aws"
  aws {
    account_id = var.aws_account_id
  }
  attribute_mapping = {
    "google.subject"     = "assertion.arn"
    "attribute.aws_role" = "assertion.arn.extract('assumed-role/{role}/')"
  }
}

resource "google_service_account" "cross_cloud" {
  account_id   = "tsar-cross-cloud"
  display_name = "TSAR cross-cloud service account"
}

resource "google_service_account_iam_binding" "cross_cloud" {
  service_account_id = google_service_account.cross_cloud.name
  role               = "roles/iam.workloadIdentityUser"
  members = [
    "principal://iam.googleapis.com/${google_iam_workload_identity_pool.cross_cloud.name}/subject/${var.aws_cross_cloud_subject}",
  ]
}

# Azure federated credential for AWS and GCP.
resource "azuread_application" "cross_cloud" {
  display_name = "tsar-cross-cloud"
}

resource "azuread_service_principal" "cross_cloud" {
  client_id = azuread_application.cross_cloud.client_id
}

resource "azuread_application_federated_identity_credential" "aws" {
  application_object_id = azuread_application.cross_cloud.object_id
  display_name          = "aws-federation"
  issuer                = "https://oidc.eks.${var.aws_region}.amazonaws.com/id/${var.eks_oidc_id}"
  subject               = "system:serviceaccount:tsar-example:tsar-app"
  audiences             = ["api://AzureADTokenExchange"]
}
