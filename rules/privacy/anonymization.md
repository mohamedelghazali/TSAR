# Anonymization and Pseudonymization

## Definitions
- **Pseudonymization**: replace identifiers with tokens; reversible with a key.
- **Anonymization**: irreversible removal of identifiability; not subject to GDPR.
- **De-identification**: reduce identifiability; often still personal data.

## Techniques
| Technique | Use | Reversible |
|---|---|---|
| Tokenization | Payment, analytics | Yes (with vault) |
| Hashing (with salt) | Correlation without identity | No |
| k-Anonymity | Datasets with quasi-identifiers | No |
| l-Diversity | Prevent attribute disclosure | No |
| Differential privacy | Aggregate queries | No |
| Synthetic data | Development, testing | No |

## Requirements
- Pseudonymization: token vault in HSM/KMS with strict access control.
- Hashing: HMAC-SHA-256 with per-purpose secret, not plain SHA-256.
- k-Anonymity: k >= 5 minimum, k >= 11 for sensitive attributes.
- Differential privacy: epsilon <= 1.0 for public releases.
- Synthetic data: statistical validation against source, no memorization.

## Verification
- Re-identification tests on released datasets.
- Statistical disclosure control review.
- Independent audit for public releases.

## Forbidden
- Plain SHA-256 for identifiers (rainbow tables).
- Reversible tokenization without key separation.
- Releasing "anonymized" data without re-identification testing.
- k < 5 in any release.
