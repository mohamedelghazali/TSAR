# TSAR Release Qualification

This document separates the historical v1.1.1 release qualification from verification of the current `main` snapshot. A successful repository CI run is not evidence of a published release or a live cloud deployment.

## Historical v1.1.1 Release

- Repository: `mohamedelghazali/TSAR`
- Version: `1.1.1`
- Tag: `v1.1.1`
- Qualified commit: `61dce3e6d46dd25dfc0ad05617329d7ba89d43a5`
- Qualified tree: `a4ba503222ceed395bdb81f48b43ebb313bbeffd`
- Snapshot reviewed: 2026-10-31
- GitHub Release: [TSAR v1.1.1 — Stable Release](https://github.com/mohamedelghazali/TSAR/releases/tag/v1.1.1)
- Published at: 2026-10-31 21:22:51 UTC

The v1.1.1 qualification below applies only to that historical source snapshot. It must not be interpreted as qualification of later commits now present on `main`.

### Historical evidence

- The inventory recorded 171 active rule files across 37 rule domains, with all manifest references resolving at that snapshot.
- The inventory recorded 15 agent-specific prompts plus the universal prompt.
- The complete release gate passed on the qualified commit; its log reported 186 pytest tests passed.
- The historical main ruleset and release status were recorded at that time.
- The GitHub Release had no separately attached binary assets; GitHub provided source archives.

The historical inventory and CI evidence are retained as release records, not asserted as a fresh inventory of the current tree.

## Current Main Snapshot — 2026-11-07

- Branch: `main`
- Commit: `7c76e8a51029b3d1f5ce979632245b71b0fc4484`
- Commit subject: `feat(worm): implement AWS S3 Object Lock anchor service (#67)`
- Version files remain at `1.1.1` (`VERSION`, `manifest.yaml`, and `tools/tsar-cli/pyproject.toml`).
- The `v1.1.1` tag does not point to this commit. The current main snapshot is therefore not represented by the published v1.1.1 tag or its historical release qualification.

### Current CI evidence

The post-merge workflows for the current main commit completed successfully:

- The current commit's release-gates workflow completed successfully.
- The full verification job reported **266 pytest tests passed** and `ALL CHECKS PASSED`.
- The post-merge check-run set was reported as **7/7 successful**.
- Terraform static validation, infrastructure validation, Kubernetes schema validation, TSAR validation, self-test, and orchestrator checks completed successfully.

This is evidence of repository-level validation for this commit. It is not evidence of a live AWS deployment or an independently audited production environment.

### Current GitHub governance

The active ruleset `TSAR-Main-Protection` targets `refs/heads/main` and currently enforces:

- Pull requests for changes to main.
- Review-thread resolution.
- No branch deletion.
- No non-fast-forward updates.
- Required linear history.
- Zero required approving reviews.

The ruleset retrieved for this review does **not** contain a required-status-checks rule. Consequently, successful CI runs are observed evidence, but this ruleset does not currently make those checks a merge prerequisite. The GitHub integration used for this review could read the ruleset but could not update it. Required status checks should be configured by a repository administrator using the exact check names produced by the workflows.

A second qualified maintainer's approval is recommended when one is available. No approval requirement is represented as active today.

## AWS WORM Service — Implementation vs. Operation

PR #67 added the AWS Lambda anchor service, Terraform infrastructure, KMS Ed25519 signing, S3 Object Lock COMPLIANCE retention, DynamoDB sequencing/idempotency, trust export tooling, and isolated behavioral/contract tests.

The following boundaries are explicit:

- The service code and infrastructure definitions are present in the repository.
- CI validates code and infrastructure statically and runs isolated tests.
- No AWS resources have been deployed by this repository change.
- No live AWS integration test has been completed.
- No AWS credentials, production secrets, or deployed endpoints are included in the repository evidence.
- S3 and DynamoDB do not share a transaction; a retained orphan S3 object can remain if the DynamoDB transaction fails.

Therefore, the AWS WORM service is an implemented deployment candidate, **not an operational or production-verified service**. Operational qualification requires an owner-approved AWS deployment and live verification of the deployed controls.

## Staging Scope

A separate Staging environment is **not a required project milestone** for TSAR. The core rules, CLI, OPA/LSP integrations, and GitHub workflows are validated through local tests and CI. If the AWS WORM service is later deployed, it can be validated in an isolated AWS account or explicitly bounded test deployment; this does not create a requirement for a permanent, general-purpose Staging environment.

## Qualification Decision

| Scope | Decision |
|---|---|
| Historical v1.1.1 release | Qualified only for its recorded tag and commit |
| Current main repository CI | Pass on `7c76e8a51029b3d1f5ce979632245b71b0fc4484` |
| Current main as a new published release | Not qualified as a new release; no new version/tag has been created |
| AWS WORM operational behavior | Not verified; no live deployment |
| Separate Staging environment | Not required |

Do not move or retarget the historical `v1.1.1` tag. A future release based on current main requires an explicit versioning/release decision and a fresh release qualification tied to the exact release commit.

This qualification does not certify absence of vulnerabilities, guaranteed agent prompt compliance, regulatory compliance, or live cloud deployment behavior.
