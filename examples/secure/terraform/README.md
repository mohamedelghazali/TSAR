# TSAR Terraform example

This directory is a security-focused infrastructure example, not a production-ready deployment module. Review costs, quotas, naming, IAM trust relationships, and environment-specific networking before applying it.

## Validation

Run formatting, provider lock generation, initialization, and validation:

```bash
terraform fmt -check
terraform providers lock -platform=linux_amd64 -platform=darwin_arm64 -platform=windows_amd64
terraform init -backend=false -lockfile=readonly
terraform validate
```

The CI workflow generates a provider lockfile from the Terraform Registry and uploads it as a workflow artifact. Commit the reviewed \`.terraform.lock.hcl\` produced by the successful run before declaring this example reproducible.

## Planning and applying

A real \`terraform plan\` requires valid AWS credentials and environment-specific values, including the EKS OIDC issuer and its verified thumbprint. CI does not run \`apply\` and must not create cloud resources. Run a plan only in an isolated AWS test account after reviewing the resource costs and permissions.

The RDS master password is managed by AWS Secrets Manager; no database password is stored in this repository.
