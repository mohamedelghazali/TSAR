# TSAR Release Qualification

This document records the evidence required before creating a stable release. A successful static check is not equivalent to a cloud deployment or production readiness.

## Current hardening branch

- Target branch: `main`
- Working branch: `release/stable-hardening-v2`
- Review: [Pull Request #3](https://github.com/mohamedelghazali/TSAR/pull/3)
- Stable release tag: not created
- Merge to `main`: not authorized by this work

## Qualification matrix

| Area | Implemented in this branch | Release evidence still required |
|---|---|---|
| CLI initialization | Staged installation, previous-tree backup, rollback path, preservation of top-level custom entries and existing agent instructions/hooks | CI must execute the success, refresh, custom-data, and simulated-promotion-failure tests |
| Standards sync | Fetch-all-before-write, fail-closed behavior, staged cache replacement, GitHub Actions outputs, no-op gating, tracked fingerprint cache | CI must execute failure/no-change/change tests; maintainers must review upstream source changes and update rule text deliberately |
| Terraform | Exact AWS provider version constraint; app-to-RDS traffic scoped by security-group reference | A multi-platform `.terraform.lock.hcl` is now committed and checked by CI; run fmt/init/validate; review a plan with authorized AWS credentials |
| Kubernetes | External TLS Secret provisioning, pinned ExternalSecret schema, explicit image and IRSA placeholders, deployment prerequisites documented | Replace placeholders with a verified immutable application image digest and actual IRSA role ARN; validate against the target cluster and External Secrets Operator |
| GitHub Actions | External actions pinned to full commit SHAs; explicit token permissions; checkout credentials not persisted; OPA and kubeconform downloads pinned and checksum-verified | All PR workflow runs must complete successfully; review any remaining third-party downloads and package installation steps |
| Governance | Contribution command corrected; custom source-available license and contribution terms documented; previous MIT grants expressly preserved | Obtain legal review before distributing a release under the new license |
| Verification | Full verification no longer installs Python packages as a side effect | Run `python3 -m pip install -r requirements-dev.txt`, then `./verify-all.sh`; record tool skips and failures |


## CI snapshot — 2026-10-31

At branch head `f6c54e2a8bf43a9651ef440f9b9b8198640de9a6`, the latest pull-request workflow set completed successfully:

- TSAR Self-Test, including the full pytest suite.
- TSAR Validate Rules and TSAR Orchestrator.
- TSAR Enforce on PR, including secret scanning and secure-example review.
- Infrastructure Validation: Terraform format, readonly initialization, multi-platform provider lock verification, unchanged-lock check, and validation; Kubernetes strict kubeconform validation with the pinned ExternalSecret schema.
- Domain-specific test workflows for backup/DR/legal hold, email/endpoint/identity, messaging/database, privacy/threat-intelligence/forensics, and compliance references.

The PR remains a draft and `main` remains at its original base commit. Passing CI does not mean a cloud plan or live Kubernetes deployment has been performed.

## Mandatory release gates

1. All required GitHub Actions checks for the release PR pass.
2. The full test suite passes, including the new CLI rollback, sync, infrastructure, workflow-pinning, and license tests.
3. A provider lock file is generated from the official Terraform registry, reviewed, committed, and verified on the platforms the project supports. Do not fabricate provider checksums.
4. Terraform formatting, initialization, and validation pass. A plan must be reviewed before any deployment. No apply is performed by this qualification process.
5. The Kubernetes image digest and IAM role ARN are replaced with real, reviewed deployment values. External Secrets Operator, ClusterSecretStore, AWS secrets, TLS certificate, ingress, DNS, and network routes are provisioned and validated in the target environment.
6. The custom license receives legal review. Previously distributed MIT copies remain governed by the MIT license grants already made; this repository change does not revoke those rights.
7. A maintainer explicitly approves the final PR and release version. Only then should a signed release tag and release notes be created.

## Known execution boundaries

No AWS credentials or target Kubernetes cluster are assumed. Therefore, no Terraform plan/apply, AWS deployment, Kubernetes apply, live TLS validation, or production readiness claim is made here. CI results must be read from the actual GitHub Actions runs; the presence of a workflow or test file is not proof that it passed.
