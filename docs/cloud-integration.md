# Cloud Integration Guide

## AWS
1. Apply `rules/cloud/aws.md` in code review.
2. Enforce via SCPs: block CloudTrail/GuardDuty/Config disable.
3. Use `examples/secure/terraform/` as a starting template.
4. Run `tsar scan` in CodeBuild or GitHub Actions.

## GCP
1. Apply `rules/cloud/gcp.md`.
2. Enforce Organization Policies for resource location and key creation.
3. Run `tsar scan` in Cloud Build.

## Azure
1. Apply `rules/cloud/azure.md`.
2. Enforce Azure Policy for storage public access and TLS minimum.
3. Run `tsar scan` in Azure DevOps pipelines.

## Multi-Cloud
1. Centralize logs at SIEM.
2. Use one identity provider for humans.
3. Enforce IaC policy-as-code across clouds.

## Verification Checklist
- [ ] No public buckets / storage accounts.
- [ ] All data stores encrypted with customer-managed keys where required.
- [ ] No long-lived credentials for workloads.
- [ ] Audit logs enabled and forwarded.
- [ ] Network defaults deny; egress restricted.
- [ ] Secret manager in use; no secrets in code or env.
