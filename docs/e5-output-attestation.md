# E5: Attested Output Verification Lifecycle

## Scope

TSAR already provides Ed25519 reviewer attestations for lifecycle gates. This integration makes the E4 output-verification result a mandatory lifecycle gate and validates its contents before a reviewer can attest it.

## Required gate

Every task plan now includes `output_verification`. It starts as `PENDING` and cannot be completed through a reviewer attestation unless the referenced E4 evidence:

- uses schema `tsar/output-evidence/v1`;
- has a valid canonical evidence digest;
- records decision `PASS`;
- includes a non-empty mandatory check set;
- records every mandatory check as `PASS` with exit code 0; and
- has no missing or failed required checks.

The lifecycle attestation then binds the exact evidence file path, SHA-256, size, task context, upstream TSAR commit, reviewer key identity, decision, timestamp and Ed25519 signature. The trusted reviewer keyring must remain outside the project root.

## Workflow

1. Initialize a strict lifecycle run. Upstream preflight is verified and pinned.
2. Run the output gate over the actual changed files and trusted required checks.
3. Save the resulting E4 JSON evidence inside the project root.
4. Have an authorized reviewer sign the generated `output_verification` attestation payload using their private Ed25519 key.
5. Record it with the lifecycle evidence command.
6. Run lifecycle verification. Completion is allowed only when every required gate and every evidence integrity check passes.

The private signing operation is intentionally external to TSAR; TSAR never stores or generates a reviewer's private key. Reviewer identity and allowed gate scope come from the externally protected trusted keyring.

## Failure behavior

A missing, malformed, modified, BLOCKED, FAIL, NOT_RUN or incomplete E4 evidence record cannot be attested as a passing output-verification gate. A valid signature cannot override a failed E4 result. A reviewer may record a signed FAIL decision, which preserves the failure rather than converting it to success.

## Assurance boundary

This is E5 lifecycle integration for the controlled CLI and audit paths covered by tests. It does not automatically force every AI provider to use the CLI, prove that the host discovered every changed file, or make local evidence storage immutable. Protect the host integration, required-check configuration, reviewer keyring and audit destination. External WORM anchoring remains an optional separate capability and is not required for this GitHub-only stage.
