# TSAR Release Qualification

This document records evidence for the stable-release decision. Passing CI checks is not equivalent to a cloud deployment or production readiness.

## Repository state — 2026-10-31

- Target branch: `main`
- Verified implementation tree baseline: `49a9c5ad4e623994b133f35cf6abe15387fb61a5` (the source tree validated by the full release gate).
- Release verification changes: [PR #7](https://github.com/mohamedelghazali/TSAR/pull/7), merged.
- Qualification evidence refresh: [PR #8](https://github.com/mohamedelghazali/TSAR/pull/8), merged.
- PR #7 changed OPA policies, CI workflows, and LSP documentation; it did not change the Terraform or Kubernetes deployment manifests.
- No stable release tag or GitHub Release was created.

## CI evidence

### Post-merge checks on main

| Workflow | Result | Evidence |
|---|---|---|
| TSAR Self-Test | 185 passed, 0 skipped | [Run 41229023489](https://github.com/mohamedelghazali/TSAR/actions/runs/41229023489) |
| OPA Policy Check | Compilation succeeded; 2 policy tests passed | [Run 41229023484](https://github.com/mohamedelghazali/TSAR/actions/runs/41229023484) |
| TSAR LSP Build | TypeScript build succeeded | [Run 41229023541](https://github.com/mohamedelghazali/TSAR/actions/runs/41229023541) |
| TSAR Orchestrator | Successful | [Run 41229023567](https://github.com/mohamedelghazali/TSAR/actions/runs/41229023567) |
| TSAR Validate Rules | Successful | [Run 41229023496](https://github.com/mohamedelghazali/TSAR/actions/runs/41229023496) |

### Full release verification

The full `verify-all.sh` gate passed on PR #7 head `88d7d59bed340fdeae4349e9b74068e8e02bce0e`. That commit and the squash merge commit on `main` have the same Git tree SHA (`78d56cbc399d97e8c41dce42c2781f126dad098e`), so the verified source tree is identical.

- 185 pytest tests passed, 0 skipped.
- OPA policy compilation passed.
- LSP build passed.
- Terraform validation passed.
- All `verify-all.sh` checks passed.

Evidence: [Full release-gates run 41228906176](https://github.com/mohamedelghazali/TSAR/actions/runs/41228906176).

The dedicated OPA and LSP workflows also passed on the same PR head:
- [OPA tests — run 41228906111](https://github.com/mohamedelghazali/TSAR/actions/runs/41228906111)
- [LSP build — run 41228906184](https://github.com/mohamedelghazali/TSAR/actions/runs/41228906184)

### Infrastructure validation scope

- The full verification gate runs Terraform formatting/validation, but does not execute a cloud-backed Terraform plan or apply.
- The earlier infrastructure workflow validated 10 Kubernetes resources against schemas. It did not contact a live cluster. PR #7 did not change Kubernetes manifests.
- Static schema validation does not prove that an EKS cluster, IRSA trust relationship, External Secrets Operator, ClusterSecretStore, secret values, TLS certificate, ingress, DNS, or network routes are configured correctly.

## Qualification matrix

| Area | Verified | Remaining gate |
|---|---|---|
| Core Python tests | 185 passed, 0 skipped on current main | Keep the OPA-enabled self-test required |
| OPA | Rego v1 compilation and 2 policy tests passed | Add broader positive/negative policy fixtures for MFA and S3 encryption before production use |
| LSP | TypeScript build passed | Runtime/editor integration testing remains optional unless the LSP is part of the release deliverable |
| Full verification | `verify-all.sh`: ALL CHECKS PASSED on a source tree identical to current main | Preserve this workflow as a required PR check |
| Terraform | Formatting and validation passed | Run `terraform plan` with authorized AWS credentials and the intended account/region; do not apply without approval |
| Kubernetes | Schema validation passed for 10 resources in the prior infrastructure run; no Kubernetes manifests changed in PR #7 | Validate IRSA, image digest, TLS, External Secrets, ingress, DNS, and network behavior against the actual target cluster |
| Branch protection | Rulesets API currently returns an empty list; earlier direct check reported `main` as unprotected | Confirm/enable PR requirement, required status checks, no force-push, and no branch deletion in repository Settings |
| License | README, CONTRIBUTING, and LICENSE identify a custom source-available license and state it is not OSI-approved; earlier MIT grants are expressly preserved | Formal legal review remains required before commercial distribution or stable release |

## Preliminary license review — not legal advice

The current repository documentation is internally consistent that TSAR is source-available, not OSI-approved open source, and that commercial use requires prior written permission and a separate commercial license. The LICENSE also says prior MIT grants are not revoked.

Items for qualified counsel and the copyright holder to resolve before release:

1. Define the boundary of "Commercial Use" and permitted use by employees, contractors, customers, integrators, universities, and public-sector entities.
2. Confirm the intended governing law, venue, dispute process, and enforceability of the warranty/liability and termination clauses in relevant jurisdictions.
3. Review the contributor grant, especially the right to sublicense contributions under separate commercial licenses, and decide whether a separate CLA or explicit contributor acceptance is needed.
4. Audit third-party code, rules, prompts, examples, trademarks, and generated materials for ownership and compatible license obligations.
5. Clarify the sample metadata in `examples/secure/docker/Dockerfile`: it labels an example image as `Apache-2.0` and uses a placeholder source URL. Confirm that this label applies only to the sample application and not to TSAR itself; otherwise correct it.
6. Consider adding an explicit patent license, trademark statement, and a contact address/process for commercial licensing.

Do not replace the custom license with MIT or another standard license without an explicit decision by the copyright holder and a rights audit.

## Mandatory remaining gates

1. Obtain authorized AWS credentials and run a reviewed Terraform plan for the intended account and region. No apply is implied.
2. Obtain access to the target Kubernetes cluster and validate the actual image digest, IRSA role ARN/trust, External Secrets resources, TLS certificate/key, ingress, DNS, and network paths. No cluster changes are implied.
3. Enable and verify branch protection or a ruleset for `main`, including required CI checks and review policy.
4. Obtain formal legal review of the custom license and third-party rights.
5. Obtain explicit maintainer approval before creating a signed stable tag or publishing release artifacts.

## Execution boundaries

No AWS credentials or target Kubernetes cluster were supplied. Therefore, no cloud-backed Terraform plan/apply, AWS deployment, Kubernetes apply, or live TLS validation was performed. The repository is not declared production-ready, and no stable release is authorized by this document.
