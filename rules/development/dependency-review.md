# Dependency Review

## Pre-Addition Checklist
- [ ] License compatible with project.
- [ ] Maintained (commit within 12 months).
- [ ] No known critical CVEs.
- [ ] Minimal dependency tree.
- [ ] Signed releases where ecosystem supports.
- [ ] Reputable maintainer or organization.

## Ongoing
- Automated dependency updates (Dependabot, Renovate).
- Security advisories monitored.
- SBOM regenerated per build.
- Vulnerability SLA:
  - Critical: 24 hours.
  - High: 7 days.
  - Medium: 30 days.
  - Low: next cycle.

## Typosquatting Defense
- Internal registry mirror with allow-list.
- Scoped packages for internal code.
- Verify package name against known-good.

## Forbidden
- Adding dependencies without review.
- Floating versions in production.
- Ignoring critical CVEs without exception.
