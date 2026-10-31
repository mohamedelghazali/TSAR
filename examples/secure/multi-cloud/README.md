# Multi-Cloud Federation Example

Demonstrates identity federation across AWS, GCP, and Azure without long-lived
credentials. Each cloud trusts the others' OIDC issuers and issues short-lived
tokens on demand.

## Flow
1. Workload in AWS assumes role via IRSA (Kubernetes ServiceAccount).
2. Workload in GCP uses Workload Identity Federation with AWS as the source.
3. Workload in Azure uses federated credentials bound to the AWS OIDC issuer.
4. All cross-cloud tokens are short-lived (<= 1 hour).
5. No static credentials stored in any cloud.

## Security Properties
- No long-lived API keys between clouds.
- Trust is anchored in OIDC issuer identity.
- Attribution preserved: each request is traceable to a workload identity.
- Rotation automatic via OIDC token refresh.

## Deployment
```bash
terraform init
terraform plan -var-file=prod.tfvars
terraform apply -var-file=prod.tfvars
```

## Requirements
- AWS account with OIDC provider for EKS.
- GCP project with Workload Identity Federation enabled.
- Azure AD tenant with app registrations allowed.
- All providers pinned to specific versions.
