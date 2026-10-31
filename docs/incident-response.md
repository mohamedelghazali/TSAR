# Incident Response

## Scope
Applies to any project using TSAR when a security incident is suspected:
secret exposure, unsafe code merged, compromised dependency, or compromised agent.

## Phase 1 — Detect
- `tsar scan` runs in CI on every PR.
- Alerting on: secret detections in main, HIGH findings, unusual agent behavior,
  unexpected manifest version changes.
- Log agent-generated code with manifest version in commit metadata.

## Phase 2 — Contain
- Revoke exposed secrets immediately (rotate keys, revoke tokens).
- If a compromised dependency is identified, pin to a known-good version.
- If an agent is compromised, disable it; freeze its outputs.
- Notify the security team; open an incident channel.

## Phase 3 — Eradicate
- Identify the root cause: rule gap, agent misconfiguration, upstream change.
- Patch rules; add the missed pattern to `rules/` and `secure-review`.
- Regenerate affected code from scratch under the updated rules.

## Phase 4 — Recover
- Restore from a verified backup if data integrity was affected.
- Re-run full scanners across the codebase.
- Re-enable the agent only after verifying it loads the current manifest.

## Phase 5 — Learn
- Update `rules/` with the missed pattern.
- Add a regression test in `tests/`.
- Update `docs/security-model.md` with the new failure mode.
- Update the threat model template if a new class of threat appeared.

## Communication
- Internal: incident channel, status updates every 2 hours.
- External: coordinate disclosure per `SECURITY.md`.
- Regulators: per applicable law (GDPR 72h, HIPAA 60 days, etc.).

## Post-Mortem Template
```markdown
# Incident Post-Mortem: <title>

## Timeline
## Impact
## Root Cause
## Detection
## Response
## What Worked
## What Failed
## Action Items
| Item | Owner | Due |
|---|---|---|
```

## Specific Scenarios

### Secret Exposure
1. Revoke and rotate immediately.
2. Audit access logs for the credential.
3. Add the pattern to `skills/secret-scanner/scanner.py`.
4. Regenerate affected code.

### Unsafe Code Merged
1. Revert the merge.
2. Fix under the correct rule.
3. Add a test that fails on the old pattern.
4. Re-run `tsar scan` before re-merging.

### Compromised Dependency
1. Pin to a known-good version.
2. Update SBOM.
3. Scan downstream consumers.
4. Review the dependency's update history for other compromises.

### Compromised Agent
1. Disable the agent.
2. Review its recent outputs (`git log` filtered by agent commits).
3. Re-enable with a stricter enforcement level.
4. Require human review for its next N commits.
```
