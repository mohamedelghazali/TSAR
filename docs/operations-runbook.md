# Operations Runbook

## Daily
- CI must pass on main.
- `auto-update-rules` workflow may open a PR; review and merge within 7 days.
- Alert on any secret detection in production branches.

## Weekly
- Review `cbom.json` diffs; ensure no new weak algorithms.
- Check agent-generated commits; sample review.
- Rotate any non-prod credentials used in tests.

## Monthly
- Re-run full scanner on default branch.
- Reconcile SBOM with actual dependencies.
- Tabletop exercise: one incident scenario from `docs/incident-response.md`.

## Quarterly
- Full restore test from backups.
- Rule efficacy review: which rules caught real findings.
- Threat model refresh for Tier-1 systems.
- Dependency audit: remove unused packages.

## Annually
- Cryptographic inventory review; plan PQC migration milestones.
- Rotate KEKs and root keys.
- Penetration test Tier-1 systems.
- Review and update `docs/security-model.md`.

## Optional AWS WORM Service Operations

The AWS WORM anchor service is not deployed by repository CI. Do not treat a successful Terraform validation or isolated test as evidence of an operational AWS deployment.

Before enabling the service:
- Obtain explicit owner approval for the target AWS account, region, resources, retention period, and expected costs.
- Review the Terraform plan and IAM permissions before applying.
- Provision the bearer token through Secrets Manager; never commit it or pass it in shell history.
- Export the KMS Ed25519 public trust file to a protected location outside the repository and independently verify its fingerprint.
- Run live integration checks for API authentication, receipt signature verification, S3 Object Lock COMPLIANCE retention, DynamoDB sequencing/idempotency, and failure/retry behavior.
- Record the deployed resource identifiers, verification evidence, retention settings, and operational owner without recording secrets.

A permanent general-purpose Staging environment is not a TSAR completion prerequisite. If AWS deployment is undertaken, use an isolated account or bounded test deployment appropriate to that operation. Do not claim production readiness until the live checks above pass.
