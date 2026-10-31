# Privacy by Design

## Seven Principles (Cavoukian)
1. Proactive not reactive.
2. Privacy as the default.
3. Privacy embedded into design.
4. Full functionality (positive-sum).
5. End-to-end security.
6. Visibility and transparency.
7. Respect for user privacy.

## Engineering Practices
- Privacy impact assessment (PIA) before new features.
- Data protection impact assessment (DPIA) for high-risk processing.
- Threat model includes privacy threats (linkability, identification).
- Default settings favor privacy.
- Privacy-preserving technologies (PETs) evaluated:
  - Homomorphic encryption for computation on encrypted data.
  - Secure multi-party computation for joint analytics.
  - Federated learning for distributed training.

## Data Flows
- Map all data flows with classification.
- Identify cross-border transfers.
- Document lawful basis per flow.
- Review third-party integrations.

## Verification
- PIA/DPIA completed and reviewed.
- Privacy tests in CI (no PII in logs, correct redaction).
- Privacy notice updated with each change.
