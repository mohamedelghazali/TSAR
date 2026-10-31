# TSAR Release Qualification

This document separates repository/CI evidence from cloud deployment evidence,
legal approval, and release authorization. A passing static pipeline is not a
production deployment certification and does not establish that a system is
free of vulnerabilities.

## Repository state — 2026-10-31

- Repository: `mohamedelghazali/TSAR`
- Target branch: `main`
- Base `main` commit before PR #14: `2df15534a40f7f67f67daa33cc9c4034c1642400`
- Base tree before PR #14: `c82943c3ed8f0e366e00d4383a4cc5104c8a9790`
- Latest main change: PR #13, adding copyright-holder contact details to
  `LICENSE`; the commit is GitHub-verified.
- Repository metadata files currently declare version **1.1.1**:
  `VERSION`, `manifest.yaml`, and `tools/tsar-cli/pyproject.toml`.
- GitHub repository description still says `tsar/v1.1.0` and must be updated
  by a repository administrator.
- No Git tags and no GitHub Releases currently exist.
- No open pull requests were present at the time of this qualification refresh.

## CI evidence

The recorded full verification run [41228906176](https://github.com/mohamedelghazali/TSAR/actions/runs/41228906176)
passed on PR #7 head `88d7d59bed340fdeae4349e9b74068e8e02bce0e`. Its source tree
matched the then-current main tree, but it predates PR #13. The recorded gate
reported 185 pytest tests passed, OPA policy compilation and two policy tests
passed, LSP build passed, and Terraform static validation passed.

Recorded post-merge main checks:
- [TSAR Self-Test — run 41229023489](https://github.com/mohamedelghazali/TSAR/actions/runs/41229023489)
- [OPA Policy Check — run 41229023484](https://github.com/mohamedelghazali/TSAR/actions/runs/41229023484)
- [TSAR LSP Build — run 41229023541](https://github.com/mohamedelghazali/TSAR/actions/runs/41229023541)
- [TSAR Orchestrator — run 41229023567](https://github.com/mohamedelghazali/TSAR/actions/runs/41229023567)
- [TSAR Validate Rules — run 41229023496](https://github.com/mohamedelghazali/TSAR/actions/runs/41229023496)

PR #13's checks were reported successful before merge. The exact current main
commit must still receive a fresh full release-gate run after this qualification
update is merged. Do not carry forward old run IDs as evidence for a new commit.

## Infrastructure verification scope

### Terraform

The CI gate performs formatting, provider-lock consistency, initialization
without a backend, and validation. It does not authenticate to AWS and does
not run a cloud-backed plan or apply.

Required external evidence before claiming AWS compatibility for a target
environment:
1. Run `terraform plan` with a dedicated least-privilege sandbox role and the
   intended AWS account and region.
2. Review the complete plan, including replacements and deletions; do not infer
   success from a plan summary alone.
3. Do not run `terraform apply` without an explicit deployment approval.
4. Store logs and plan artifacts securely; Terraform plans can contain secrets.

### Kubernetes

Schema validation is static and does not prove live cluster behavior. It does
not establish that EKS, IRSA trust, External Secrets Operator, AWS Secrets
Manager access, TLS, ingress, DNS, or network routes work.

A live EKS qualification must verify:
- expected workload images and immutable image digests;
- ServiceAccount annotation and IRSA role trust conditions;
- successful ExternalSecret reconciliation and target Secret creation;
- TLS Secret/certificate validity and ingress behavior;
- Pod readiness, events, logs, and application health;
- least-privilege AWS access and absence of secret leakage.

Minikube can validate generic Kubernetes behavior but cannot by itself prove
EKS IRSA integration.

## GitHub governance

Two active repository rulesets currently target `refs/heads/main`:

- [TSAR-Main-Protection](https://github.com/mohamedelghazali/TSAR/rules/26284361)
- [TSAR Protect Main Branch](https://github.com/mohamedelghazali/TSAR/rules/26285137)

They overlap but are not identical. The first requires stale-review dismissal
and review-thread resolution; the second does not. Both require status checks,
including `Infrastructure Validation`. Keep one authoritative ruleset after
reviewing its complete policy and remove the duplicate through GitHub Settings
or an authorized ruleset-management interface. Do not weaken protection while
doing so.

The infrastructure workflow previously used pull-request path filters while
its check was required by the rulesets. That can leave a required check absent
on unrelated PRs. This qualification change removes those path filters and
adds manual dispatch so the check is emitted consistently. Confirm the
resulting check context in the PR checks before retaining it as required.

The rulesets currently require zero approving reviews. PR-only merging is
enforced, but independent human review is not. Decide whether at least one
approval should be required for security-sensitive changes.

## License and legal review

The repository uses a custom source-available license. It is not an
OSI-approved Open Source license, and commercial use requires prior written
authorization and a separate commercial license. The license states that
previously granted MIT rights are not revoked.

This document is not a legal opinion. Before commercial distribution or a
stable public release, the copyright holder and qualified counsel should
confirm:
1. The scope and enforceability of the Commercial Use definition.
2. Treatment of employees, contractors, customers, integrators, education,
   public-sector use, hosted services, and paid training.
3. Governing law, venue, dispute resolution, termination, warranty, and
   liability clauses in relevant jurisdictions.
4. Contributor rights and the sublicensing grant; determine whether a CLA or
   explicit contributor acceptance is needed.
5. Ownership and license compatibility of third-party code, examples, rules,
   prompts, generated materials, and trademarks.
6. Whether patent and trademark provisions and a commercial licensing process
   should be added.

Do not replace the custom license with MIT or another license without an
explicit rights-holder decision and a rights audit.

## Versioning and release decision

The checked-in codebase is version **1.1.1**. The roadmap's v2.0 items are
proposed and are not implemented in the current tree. Therefore, creating a
`v2.0.0` tag now would misrepresent the delivered scope. Do not create that
tag or publish a stable v2.0.0 release on the basis of the current evidence.

A release candidate should use the actual 1.x release line and be clearly
marked pre-release only after all repository checks pass. A stable release
requires, at minimum:
1. A fresh full CI gate on the exact release commit.
2. A consistent version in all metadata, documentation, and repository
   description.
3. One reviewed, authoritative main-branch ruleset and verified required checks.
4. Rights-holder approval of the license text and legal review appropriate to
   the intended distribution.
5. A documented decision on whether AWS/EKS live verification is required for
   the product being released. If advertised as validated deployment examples,
   complete the live tests; otherwise clearly label them as unverified examples.
6. Explicit maintainer authorization before creating a stable tag and release.

## Current decision

**NO-GO for v2.0.0 Stable.** The repository has meaningful passing CI evidence,
but the checked-in version is 1.1.1, v2.0 scope is proposed rather than
implemented, cloud-backed AWS/EKS checks have not been performed, legal
approval has not been recorded, and duplicate branch rulesets remain active.

No AWS credentials or target EKS cluster were supplied. No cloud plan/apply,
Kubernetes apply, live TLS check, legal sign-off, stable tag, or GitHub Release
has been performed by this qualification process.
