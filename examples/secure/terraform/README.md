# TSAR Terraform Example

Reference AWS deployment with:
- Encrypted S3 with public access blocked.
- RDS with encryption, private networking, IAM auth.
- KMS key with rotation and scoped policy.
- IAM role with least privilege and IRSA.
- Security groups restricting ingress.

## Usage
```bash
terraform init
terraform plan -var="environment=dev"
terraform apply -var="environment=dev"
```

## Requirements
- Remote state in encrypted S3 with DynamoDB lock.
- Provider versions pinned.
- Policy-as-code (OPA/Conftest) enforced in CI.
