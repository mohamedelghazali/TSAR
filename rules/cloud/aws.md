# AWS Security Baseline

## Identity and Access
- IAM users: no long-lived access keys; use IAM Identity Center for humans.
- Workloads: IAM roles with least privilege; no wildcard actions on production.
- Permission boundaries on all human-assumable roles.
- SCPs to prevent disabling CloudTrail, GuardDuty, Config, and Security Hub.

## Networking
- VPC with private subnets for compute; NAT for egress only.
- Security groups: deny by default; explicit ingress.
- VPC Flow Logs to S3 with retention >= 1 year.
- Private endpoints (VPC Endpoints) for AWS services.

## Compute
- EC2: IMDSv2 required, no public IPs, SSM Session Manager (no SSH).
- Lambda: execution role least privilege, no `*` resources, secrets via Secrets Manager.
- ECS/EKS: private registries, image signing, no privileged containers.

## Storage
- S3: Block Public Access enabled, SSE-KMS default, versioning on, Object Lock for critical buckets.
- EBS: encrypted by default; snapshots encrypted.
- RDS: encrypted at rest, TLS required, no public endpoints.

## Logging and Monitoring
- CloudTrail in all regions, tamper-proof S3 bucket, MFA delete.
- GuardDuty, Security Hub, Config rules enabled.
- VPC Flow Logs and DNS logs forwarded to SIEM.

## KMS
- CMKs per application, not shared.
- Automatic rotation enabled.
- Key policies restrict `kms:*` to a dedicated key-admin role.

## Secrets
- Secrets Manager for rotation.
- Never in Parameter Store plaintext for sensitive values.

## Forbidden
- Root account usage beyond billing.
- IAM users with `Action: "*"` on `Resource: "*"`.
- Public S3 buckets.
- Unencrypted RDS or EBS.
