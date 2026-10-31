# TSAR Release Qualification

This document records repository evidence and owner decisions for the v1.1.1 release. It distinguishes automated repository checks from external approvals and deployment validation.

## Repository Snapshot

- Repository: mohamedelghazali/TSAR
- Default branch: main
- Qualified main commit: 61dce3e6d46dd25dfc0ad05617329d7ba89d43a5
- Qualified tree: a4ba503222ceed395bdb81f48b43ebb313bbeffd
- Snapshot reviewed: 2026-10-31
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

The complete release gate passed on qualified main commit 61dce3e6d46dd25dfc0ad05617329d7ba89d43a5:

- [TSAR Complete Release Gates — 41242004036](https://github.com/mohamedelghazali/TSAR/actions/runs/41242004036) — success; complete verify-all.sh suite.
- [TSAR Self-Test — 41242003931](https://github.com/mohamedelghazali/TSAR/actions/runs/41242003931) — success.
- [Infrastructure Validation — 41242003985](https://github.com/mohamedelghazali/TSAR/actions/runs/41242003985) — success.
 
The complete verification log reports **186 pytest tests passed**, successful rule linting, compliance-reference checks, secret scanning with no secrets found, orchestrator and report generation, OPA policy checks, LSP build, and Terraform validation. The separate infrastructure workflow also passed Terraform static validation and Kubernetes schema validation.

The release-gates workflow runs on every pull request to main, every push to main, and manual dispatch. This prevents a path filter from silently omitting the full release gate on documentation-only or other changes.

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

- **AWS workstream:** accepted as complete by the project owner. This records the owner's project decision; repository static Terraform and Kubernetes checks are not represented as live AWS/EKS deployment evidence.
- **License review:** the project owner confirms that the license was reviewed with an advisor and approved. This record reflects that owner confirmation; it is not an independent legal opinion.
- The repository retains its custom source-available license. It is not an OSI-approved Open Source license. Commercial use remains subject to the written authorization and commercial licensing terms in LICENSE.

## Published Version and Release

- Current declared version: **1.1.1**.
- Git tag: **v1.1.1** — published and resolves to qualified commit 61dce3e6d46dd25dfc0ad05617329d7ba89d43a5.
- GitHub Release: [TSAR v1.1.1 — Stable Release](https://github.com/mohamedelghazali/TSAR/releases/tag/v1.1.1).
- Release status: published; not a draft and not marked as a pre-release.
- Published at: 2026-10-31 21:22:51 UTC.
- The release currently has no separately attached binary assets. GitHub provides the source archives for the tag.
- The v2.0 roadmap is proposed work, not the current implementation. Do not publish v2.0.0 from the current 1.1.1 codebase.

The published tag was checked against the qualified commit. The release tag and the tested main tree therefore identify the same source snapshot.

## Qualification Decision

**Repository qualification: PASS for the published v1.1.1 release.**

The inventory is consistent, the complete release gate passed, the required CI workflows passed, the main-branch ruleset is active, the project owner has confirmed the AWS and license workstreams as complete, and the stable v1.1.1 tag and GitHub Release are published.

This qualification does not certify the absence of vulnerabilities, provider prompt compliance, regulatory compliance, or live cloud deployment behavior.
