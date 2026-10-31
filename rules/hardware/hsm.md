# HSM Integration Rules

## Key Lifecycle
- Keys generated inside HSM; never exported in plaintext.
- Rotation policy enforced by HSM configuration.
- Separation of duties: key custodian != key user.

## Operations
- All cryptographic operations logged with caller identity.
- Rate limits on signing and decryption.
- Quorum approval for key deletion or export.

## Network
- HSM accessed over mutually authenticated, dedicated network segment.
- No direct internet exposure.
