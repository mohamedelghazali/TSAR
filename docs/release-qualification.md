# TSAR Release Qualification

This document records the repository evidence and owner decisions relevant to the current release. It distinguishes automated repository checks from external approvals and deployment validation.

## Repository Snapshot

- Repository: mohamedelghazali/TSAR
- Default branch: main
- Snapshot reviewed: 2026-10-31
- Main commit reviewed before this qualification update: f784a16c135f47c6665fef1554afabf67d2d11f9
- Repository visibility: public
- Repository description: aligned with the AI security governance identity.
- Active main-branch rulesets: one (TSAR-Main-Protection).

## Verified Inventory

The repository tree and manifest were compared:

- **171 active rule files** are referenced by manifest.yaml.
- Those files cover **37 rule domains**.
- All 171 manifest rule references resolve to existing files.
- rules/blockchain/README.md is an overview file, not an active rule.
- **15 agent-specific prompts** exist, plus prompts/universal.md.
- The compatibility matrix lists the same 15 named agents.
- VERSION, manifest.yaml, and tools/tsar-cli/pyproject.toml consistently declare version **1.1.1**.

The rule-file count is an inventory measure. It does not mean that every individual rule has been independently validated against every language, framework, or agent.

## CI Evidence

On the reviewed main commit f784a16c135f47c6665fef1554afabf67d2d11f9, these push workflows completed successfully:

- [TSAR Self-Test — 41238606312](https://github.com/mohamedelghazali/TSAR/actions/runs/41238606312)
- [TSAR Orchestrator — 41238606310](https://github.com/mohamedelghazali/TSAR/actions/runs/41238606310)
- [Infrastructure Validation — 41238606307](https://github.com/mohamedelghazali/TSAR/actions/runs/41238606307)
- [TSAR Validate Rules — 41238606299](https://github.com/mohamedelghazali/TSAR/actions/runs/41238606299)

PR #16 also passed its configured pull-request checks before merge. However, the complete verify-all.sh workflow was path-filtered and did not run for that README-only change. This qualification update removes that path filter, adds push on main and workflow_dispatch, and makes the full release gate run for all pull requests and main-branch updates.

A successful workflow must be checked on the exact commit being qualified. Do not reuse older run IDs as evidence for a newer commit.

## Agent Integration and Enforcement Scope

TSAR has 15 agent-specific instruction files and one universal fallback. These integrations deliver policy guidance through each product's available project or system-instruction mechanism. They are not privileged native provider controls, and prompt compliance cannot be guaranteed.

Deterministic repository-level checks require the adopting team to configure and run TSAR scanners, hooks, and CI integrations. TSAR does not guarantee vulnerability-free output and does not replace human security review.

## GitHub Governance

The current active ruleset, TSAR-Main-Protection, targets refs/heads/main. It blocks deletion and non-fast-forward updates, requires pull requests, requires resolution of review threads, and requires these status checks:

- TSAR Self-Test
- TSAR Orchestrator
- TSAR Validate Rules
- TSAR Enforce on PR
- Infrastructure Validation
- Compliance Reference Check

The ruleset currently requires **zero approving reviews**. PR-based changes are enforced, but independent human approval is not. For a security product, one approving review is recommended when a second qualified maintainer is available. The current ruleset is the only active ruleset found; the previously duplicated main ruleset is no longer active.

## Owner Decisions and External Workstreams

- **AWS workstream:** accepted as complete by the project owner. This records the owner's project decision; the repository's static Terraform and Kubernetes checks are not represented as live AWS/EKS deployment evidence.
- **License review:** the project owner confirms that the license was reviewed with an advisor and approved. This record reflects that owner confirmation; it is not an independent legal opinion.
- The repository retains its custom source-available license. It is not an OSI-approved Open Source license. Commercial use remains subject to the written authorization and commercial licensing terms in LICENSE.

## Version and Release

- Current declared version: **1.1.1**.
- No Git tags or GitHub Releases were present in the reviewed repository.
- The v2.0 roadmap is proposed work, not the current implementation.
- Do not publish v2.0.0 from the current 1.1.1 codebase.
- A stable v1.1.1 release may be created only after the complete verify-all.sh release gate passes on the exact final main commit and the release contents are checked against the 1.1.1 changelog.

## Qualification Decision

**Repository readiness: conditionally qualified for the 1.1.1 release line.**

The repository inventory is consistent, the current required CI workflows passed on the reviewed main commit, one main-branch ruleset is active, and the project owner has confirmed the AWS and license workstreams as complete.

**Remaining automated gate:** a fresh full verify-all.sh run on the exact final commit. The release-gates workflow is being updated to run for every PR and every push to main, rather than only selected file paths. Do not create the stable tag or GitHub Release until that run succeeds.

This qualification does not certify the absence of vulnerabilities, provider prompt compliance, regulatory compliance, or live cloud deployment behavior.
