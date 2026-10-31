# TSAR Release Qualification

This document records the evidence required before creating a stable release. Passing static checks is not equivalent to a cloud deployment or production readiness.

## Repository state — 2026-10-31

- Target branch: `main`
- Current main commit: `79703ffe089d5b8124944895f128034b14b33f6a`
- Release-hardening PR: [#3 — Release hardening v2](https://github.com/mohamedelghazali/TSAR/pull/3)
- PR #3: merged; merge commit is the current main commit above.
- This qualification document is being updated separately; no deployment or release tag is created by this update.

## CI evidence on current main

The following GitHub Actions runs completed successfully for the current main commit:

| Workflow | Result | Evidence |
|---|---|---|
| TSAR Self-Test | 183 passed, 2 skipped | [Run 41223591256](https://github.com/mohamedelghazali/TSAR/actions/runs/41223591256) |
| Infrastructure Validation — Terraform | fmt, init, provider lock verification, validate passed | [Run 41223591167](https://github.com/mohamedelghazali/TSAR/actions/runs/41223591167) |
| Infrastructure Validation — Kubernetes | 10 resources valid; 0 invalid, errors, or skipped | [Run 41223591167](https://github.com/mohamedelghazali/TSAR/actions/runs/41223591167) |
| TSAR Orchestrator | 4 steps passed | [Run 41223591136](https://github.com/mohamedelghazali/TSAR/actions/runs/41223591136) |
| TSAR Validate Rules | Manifest valid; secret scanner found no secrets | [Run 41223591133](https://github.com/mohamedelghazali/TSAR/actions/runs/41223591133) |

The merged PR #3 also had successful PR-triggered runs for the full pytest suite, rule validation, orchestrator, PR enforcement, domain-specific tests, compliance references, Terraform validation, and strict Kubernetes schema validation.

### Scope and limits of the current CI

- Terraform CI runs formatting, backend-disabled initialization, provider lock verification, and configuration validation. It does **not** run a cloud-backed plan or apply.
- Kubernetes CI validates schemas only. It does **not** contact a target cluster or prove that AWS resources, the External Secrets Operator, referenced secrets, certificates, image, IAM role, ingress, DNS, or network routes exist.
- The repository's `verify-all.sh` is broader than the current `test.yml` workflow. The latest main CI evidence above does not establish that every optional check in `verify-all.sh` ran.
- The policy-specific OPA workflow and LSP build workflow are path-filtered; their absence from the latest main push run list is not evidence that they ran on this commit.
- Branch protection / ruleset enforcement could not be verified through the available GitHub integration. Confirm required status checks and review requirements in repository Settings before relying on them.

## Qualification matrix

| Area | Verified | Still required |
|---|---|---|
| Core tests | Current main: 183 passed, 2 skipped | Review the two skips and run the complete release verification script |
| Rule and manifest integrity | Current main workflow passed | Continue checking rule coverage and upstream source changes |
| Secret scanning | Current main repository scan passed | Maintain scanning on every proposed change and review scanner limitations |
| Orchestrator | Current main: 4 steps passed | Review generated reports and ensure each production integration is exercised |
| Terraform | Format, init, lock file and validate passed | Review a plan using authorized AWS credentials; do not apply without approval |
| Kubernetes | Strict schema validation passed for all 10 resources | Supply a verified immutable image digest and real IRSA role ARN; validate against the target cluster |
| External secrets and TLS | ExternalSecret schemas validated | Provision the operator, ClusterSecretStore, AWS secret entries and matching TLS certificate/key outside Git |
| GitHub Actions | External actions are pinned to full commit SHAs; workflows declare explicit permissions and disable persisted checkout credentials | Confirm required checks and branch protection/rulesets in repository settings; exercise path-filtered workflows |
| Governance | Custom source-available terms and prior MIT grant treatment are documented | Obtain legal review before commercial distribution or a stable release |

## Mandatory release gates

1. Run `python3 -m pip install -r requirements-dev.txt` and then `./verify-all.sh` in a clean environment. Record every PASS, FAIL, and SKIP; do not describe skipped checks as passed.
2. Review the two skipped pytest tests and determine whether they are expected for the release environment.
3. Confirm that OPA policy compilation/tests and the LSP build pass for the release candidate, even if their path-filtered workflows did not run on the latest main push.
4. Confirm repository branch protection or rulesets require the intended status checks and review approvals.
5. Review a Terraform plan with authorized AWS credentials and the intended target account/region. No apply is implied by this qualification process.
6. Replace the Kubernetes image placeholder with a built, scanned, published and verified immutable SHA-256 digest. Replace the IRSA placeholder with the actual role ARN and validate the trust relationship.
7. Provision and verify the External Secrets Operator, ClusterSecretStore, AWS Secrets Manager entries, matching TLS certificate/key, ingress, DNS, and required network routes in the target environment.
8. Obtain legal review of the custom source-available license. Previously distributed MIT copies remain governed by their existing MIT grants.
9. Obtain explicit maintainer approval before creating a signed stable release tag and publishing release artifacts.

## Execution boundaries

No AWS credentials or target Kubernetes cluster are assumed. Therefore, no Terraform plan/apply, AWS deployment, Kubernetes apply, live TLS validation, or production-readiness claim is made here. CI results must be read from the actual GitHub Actions runs; the presence of a workflow or test file is not proof that it passed.
