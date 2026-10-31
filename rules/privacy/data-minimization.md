# Data Minimization

## Principle
Collect only what is strictly necessary for the stated purpose. Every field
must have a documented justification and a retention period.

## Data Inventory
- Every system maintains a data inventory listing:
  - Field name, type, classification.
  - Purpose of collection.
  - Legal basis (contract, consent, legitimate interest, legal obligation).
  - Retention period.
  - Recipients and processors.
  - Cross-border transfers.
- Inventory reviewed quarterly.

## Collection
- Forms collect only required fields; optional fields clearly marked.
- No silent collection via analytics, SDKs, or third-party scripts.
- Privacy notice at point of collection.
- Consent: opt-in, granular, revocable.

## Processing
- Purpose limitation: no secondary use without a new legal basis.
- Pseudonymization where identity is not required.
- Aggregation before analytics whenever possible.

## Retention
- Per data class:
  - Transactional: 7 years (financial) or per regulation.
  - Behavioral: 90 days.
  - Marketing: until consent withdrawn.
  - Logs: 90 days hot, 1 year cold.
- Automated deletion enforced; manual exceptions tracked.

## Forbidden
- Collecting fields "just in case".
- Retaining data past its purpose.
- Using data for a purpose not disclosed.
- Silent third-party data collection.
