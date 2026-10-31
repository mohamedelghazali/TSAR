# Feature Store Security

## Data Classification
- Every feature tagged with classification (public, internal, confidential, restricted).
- PII features: tokenized or hashed at ingest.
- Features derived from PII inherit the classification.

## Access Control
- Row-level access control per tenant.
- Feature-level access control per role.
- Time-travel queries restricted to authorized users.

## Integrity
- Feature definitions versioned in Git.
- Point-in-time correctness verified on every schema change.
- Training-serving skew detected via parity checks.

## Poisoning Defense
- Statistical anomaly detection on feature drift.
- Source reputation and provenance tracking.
- Quarantine on anomalous batches before serving.

## Retention
- Per-feature TTL enforced by policy.
- GDPR/CCPA deletion propagates to feature store and offline replicas.

## Forbidden
- Serving unvalidated features to production models.
- Sharing feature store credentials across teams.
