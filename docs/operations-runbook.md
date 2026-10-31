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
