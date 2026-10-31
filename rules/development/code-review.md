# Code Review Security

## Reviewer Responsibilities
- Check for input validation on every user-controlled field.
- Verify authorization on every endpoint.
- Confirm secrets are not hardcoded.
- Verify crypto uses approved algorithms.
- Check error handling does not leak internals.
- Verify logs do not contain PII or secrets.

## Required Reviewers
| Change Area | Reviewer |
|---|---|
| Auth, crypto | Security team |
| PII handling | Privacy + Security |
| Infrastructure | Platform + Security |
| Data model | Data owner + Security |

## Process
- At least one security-aware reviewer for sensitive changes.
- Pair review for high-risk changes (auth, payments).
- Tests required for security-relevant changes.
- Comments must be resolved, not just acknowledged.

## Automation
- SAST/SCA/secrets run pre-review.
- Findings block merge if HIGH.
- False positives require documented suppression with expiry.

## Forbidden
- Self-approval for sensitive changes.
- Merge with unresolved security findings.
- Suppressions without expiry.
