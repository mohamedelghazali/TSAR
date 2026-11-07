# TSAR CLI

## Commands

| Command | Description |
|---|---|
| `tsar scan [path] [--format text\|sarif]` | Secret + secure review |
| `tsar inventory [path]` | Cryptographic inventory |
| `tsar lint` | Validate TSAR rules |
| `tsar version` | Compare local/remote manifest version |
| `tsar drift` | Detect drift between local and remote manifest (legacy version/file-set comparison) |
| `tsar agent-gate [--domain NAME] -- COMMAND [ARGS...]` | Fail-closed preflight gate before launching a controlled agent command; exports pinned provenance via environment variables |\n| `tool_boundary.ToolBoundary` | Python dispatch API for registered tools; enforces action/resource/scope checks, action-bound approvals, and audit events before dispatch |\n| `tsar verify-upstream [--domain NAME]` | Pin upstream to one commit, validate manifest and all active paths, and fetch core plus selected domain rules (fail-closed) |
| `tsar threat-model <file>` | STRIDE threat model |
| `tsar lifecycle-plan <task> [--domain NAME] [--impact auto\|standard\|high]` | Create a deterministic lifecycle plan; does not execute or approve work |
| `tsar lifecycle-start <task> --audit-file PATH [--domain NAME]` | Start a lifecycle run after upstream preflight |
| `tsar lifecycle-evidence --audit-file PATH --gate NAME --evidence PATH --attestation PATH --trusted-reviewers PATH` | Attach authenticated, evidence-backed reviewer approval to a lifecycle gate |
| `tsar lifecycle-verify --audit-file PATH --trusted-reviewers PATH` | Verify lifecycle evidence, reviewer signatures, and gate completeness |
| `tsar lifecycle-anchor --audit-file PATH --trusted-reviewers PATH --endpoint URL --service-trust PATH` | Append a verified lifecycle snapshot to an external signed WORM service |
| `tsar lifecycle-anchor-verify --audit-file PATH --trusted-reviewers PATH --endpoint URL --service-trust PATH` | Verify the latest external WORM receipt against the local audit |
| `tsar report [path] [--format html\|json]` | Full report |
| `tsar compliance <framework>` | Compliance reference check |
| `tsar init [path] --agent <name>` | Bootstrap TSAR into a project |

## Examples

```bash
tsar scan .
tsar scan . --format sarif --output results.sarif
tsar report . --format html --output report.html
tsar compliance soc2
tsar drift
tsar verify-upstream --domain api --domain iam
tsar lifecycle-plan "Implement OAuth login API" --domain iam --domain api
tsar lifecycle-start "Implement OAuth login API" --domain iam --domain api --audit-file .tsar/runs/oauth-login.json
tsar init . --agent cursor
```

## Exit Codes

- 0: clean.
- 1: findings or drift.
- 2: verification/tooling failure (preflight fails closed).

## Lifecycle audit verification

Run `tsar lifecycle-verify --audit-file .tsar/runs/run.json --trusted-reviewers C:/secure/tsar/trusted-reviewers.json` to re-hash every evidence file and verify each Ed25519 reviewer signature against an external trust keyring. Exit code 0 means evidence integrity is valid and every lifecycle gate is complete. Exit code 1 means invalid evidence, an incomplete lifecycle, or a signed FAIL decision; inspect `integrity_status` and `lifecycle_status` separately. Exit code 2 means the audit or trust store could not be verified.

## Authenticated lifecycle evidence

A gate can no longer be approved by supplying an arbitrary `--actor` label. `lifecycle-evidence` requires a detached Ed25519 signature and an external trusted reviewer keyring. The keyring maps key IDs to reviewer labels, raw Ed25519 public keys (Base64), active status, and permitted gate names:

```json
{
  "schema": "tsar/trusted-reviewers/v1",
  "keys": [{
    "key_id": "security-reviewer-01",
    "actor": "reviewer@example.org",
    "public_key": "BASE64_RAW_32_BYTE_ED25519_PUBLIC_KEY",
    "allowed_gates": ["core_policy_review", "independent_security_review"],
    "active": true
  }]
}
```

Keep this keyring outside the repository, restrict write access (POSIX mode 0600 or stricter), and protect private keys separately. The reviewer signs the canonical UTF-8 JSON representation of the payload (sorted keys, compact separators, no ASCII escaping). The payload must contain schema `tsar/reviewer-attestation-payload/v1`, audit path and a `tsar/lifecycle-context/v1` SHA-256 binding, upstream commit, gate, decision, key ID, reviewer identity, evidence path/hash/size, and timezone-aware issue time. The context binding covers all immutable run fields and the exact gate-name set while excluding mutable gate decisions and evidence entries. The signed envelope schema is `tsar/reviewer-attestation/v1` and contains `key_id`, `payload`, and Base64 `signature`.

The payload can be prepared with `build_attestation_payload()` from `lifecycle_evidence.py`; sign its canonical JSON bytes with the trusted key's Ed25519 private key, then store the envelope JSON as the `--attestation` file. The verifier derives the actor from the external keyring; it never trusts an actor string supplied on the command line.

Example:

```bash
tsar lifecycle-evidence --audit-file .tsar/runs/run.json --gate core_policy_review --evidence evidence/core-review.md --attestation evidence/reviewer-attestation.json --trusted-reviewers C:/secure/tsar/trusted-reviewers.json
tsar lifecycle-verify --audit-file .tsar/runs/run.json --trusted-reviewers C:/secure/tsar/trusted-reviewers.json
```

Legacy attestations without the lifecycle-context binding are intentionally reported as unauthenticated and must be regenerated. An empty evidence list with pending gates is reported as `INCOMPLETE`, never as a successful completed run. The verifier also requires the persisted gate map to match the exact unique `required_gates` list in the strict task plan; omitted, injected, duplicate, or malformed gates fail closed. `integrity_status` reports cryptographic/evidence consistency; `lifecycle_status` reports `COMPLETE`, `IN_PROGRESS`, or `FAILED`; overall `status` is `PASS` only when both integrity is valid and every gate is complete. Legacy unsigned evidence is intentionally reported as unauthenticated. A valid signature proves possession of a trusted private key and authorization encoded in the external keyring; it does not independently prove the human's identity, evidence truth, reviewer independence, or organizational authority. Protect the keyring and private keys with an independently administered process. The audit record remains locally mutable/deletable; signed events or an external append-only log are still required for tamper resistance.

## Lifecycle planning boundaries

`lifecycle-plan` is a deterministic planning aid. Keyword classification can miss context or select extra domains; operators must confirm the applicable domains and impact before implementation. A plan is not a security approval, does not execute scanners, and does not mark gates as passed. High-impact tasks require the listed additional review gates.

## External WORM audit anchoring

TSAR can submit a locally verified lifecycle audit snapshot to an independently administered HTTPS anchor service. The client accepts only a signed receipt from a separately pinned Ed25519 service key and requires the receipt to attest `WORM_COMPLIANCE` retention with a future `retain_until` timestamp. The service must enforce create-only append semantics, atomic compare-and-append using `expected_previous_anchor_sha256`, durable retention, and an authenticated latest-record lookup. A signed receipt is not, by itself, proof that the service's storage configuration is genuinely immutable; independently audit the service and its storage policy.

### Trust and credentials

Keep the service trust file outside the repository and restrict write permissions (POSIX mode 0600 or stricter). It has this format:

```json
{
  "schema": "tsar/audit-anchor-trust/v1",
  "service_id": "company-worm-vault-prod",
  "public_key": "BASE64_RAW_32_BYTE_ED25519_SERVICE_PUBLIC_KEY"
}
```

Set the bearer token in the environment variable `TSAR_AUDIT_ANCHOR_TOKEN`; never put it in command-line arguments, audit files, or source control. The service public key must be obtained and verified through an independent administrative channel.

### Commands

```bash
# Append the current verified snapshot; the receipt file is create-only.
tsar lifecycle-anchor --audit-file .tsar/runs/run.json --trusted-reviewers C:/secure/tsar/trusted-reviewers.json --endpoint https://worm.example --service-trust C:/secure/tsar/anchor-service.json --receipt .tsar/receipts/run-anchor.json

# Verify that the remote latest anchor matches the current local audit bytes.
tsar lifecycle-anchor-verify --audit-file .tsar/runs/run.json --trusted-reviewers C:/secure/tsar/trusted-reviewers.json --endpoint https://worm.example --service-trust C:/secure/tsar/anchor-service.json
```

### Required service API contract

- `GET /v1/runs/{run_id}/latest`: return HTTP 200 with `{"receipt": ...}`, or HTTP 404 when no anchor exists.
- `POST /v1/anchors`: atomically append the request and return HTTP 201 with `{"receipt": ...}`. Reject a stale `expected_previous_anchor_sha256`; enforce the idempotency key; never overwrite or delete prior records.
- The signed receipt schema is `tsar/external-audit-anchor-receipt/v1`. Its Ed25519 signature covers every receipt field except `signature`. Required fields: `service_id`, `anchor_id`, `run_id`, positive `sequence`, `record_sha256`, `previous_anchor_sha256`, timezone-aware `anchored_at`, `retention_mode` equal to `WORM_COMPLIANCE`, and future timezone-aware `retain_until`.
- The service must store every append in independently administered WORM/COMPLIANCE storage with retention lock, preserve all versions, and prevent privileged deletion during retention. It must not merely echo the requested retention mode.
- Protect transport with TLS, authenticate clients, rotate credentials, monitor retention-policy drift, and retain service signing keys in a separate KMS/HSM or equivalent trust boundary.

The anchor client refuses incomplete or invalid evidence integrity, rejects redirects, refuses non-HTTPS endpoints, verifies the service signature and retention claim, and detects stale/missing latest snapshots. The local receipt is a convenience copy, not the authoritative archive. No external service is provisioned by TSAR itself; anchoring is operational only after an independently administered service implementing this contract is deployed and configured. A compromised service signing key or dishonest service administrator remains a trust-boundary risk.
\n\n## Tool boundary integration (E3 building block)\n\nImport `ToolBoundary`, `ToolSpec`, `ActionRequest`, and `AuthorizationContext` from `tool_boundary`. Register tools in trusted host code and route every actual tool call through `ToolBoundary.dispatch`. The host must supply an authenticated principal, least-privilege scopes, a verifier for single-action approvals, and a durable audit sink. Unknown tools and out-of-scope actions fail closed. Credential access, deployment, irreversible actions, and explicitly approval-gated tools require a verified approval bound to the exact action digest. See `docs/tool-boundary-adapter.md` for the trust contract and limitations.\n\nThis API does not automatically intercept provider tools, sandbox child processes, or prevent bypass calls. Claim E3 only for host dispatch paths demonstrably routed through the boundary.\n