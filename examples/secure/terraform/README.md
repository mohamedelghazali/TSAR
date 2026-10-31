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
- AWS provider constrained to exact version 5.40.0; a committed lock file with checksums is still required.
- Policy-as-code (OPA/Conftest) enforced in CI.


## Provider lock file

Before using this example, generate and review a lock file from the official
Terraform Registry for every platform used by your team:

```bash
terraform providers lock \
  -platform=linux_amd64 \
  -platform=windows_amd64 \
  -platform=darwin_arm64
```

Commit `.terraform.lock.hcl` after verifying the selected provider version
and checksums. Do not hand-write or invent checksum entries. Keep the
`.terraform/` working directory and state files out of version control.

The example's CI currently runs initialization with backend disabled and
validates configuration only. It does not create a cloud plan or apply changes.
