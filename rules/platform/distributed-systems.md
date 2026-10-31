# Distributed Systems Security

## Service Identity
- mTLS between all services; no plaintext internal traffic.
- SPIFFE/SPIRE or equivalent workload identity.
- Per-service keys, never shared across services.

## Data
- Encryption in transit (mTLS) and at rest (per-tenant keys).
- Tamper-evident audit log (hash chain or Merkle tree).
- Data residency controls per region.

## Consensus
- Signed messages in consensus protocols.
- Quorum protected against Byzantine faults where required.

## Observability
- Structured logs with redaction of secrets and PII.
- Distributed tracing with sensitive-field scrubbing.
