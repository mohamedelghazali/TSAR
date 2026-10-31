# Disk Encryption

## Platforms
| Platform | Technology |
|---|---|
| macOS | FileVault 2 (XTS-AES-128 or -256) |
| Windows | BitLocker (XTS-AES-128 or -256) |
| Linux | LUKS2 (AES-256-XTS) |
| iOS | Data Protection (hardware) |
| Android | File-Based Encryption (hardware) |

## Key Management
- Recovery keys escrowed in MDM or KMS.
- Multi-party approval for recovery key access.
- Rotate recovery keys on personnel change.

## Verification
- Continuous compliance check via MDM.
- Alert on disabled encryption.
- Block access to corporate resources if encryption disabled.

## Forbidden
- Unencrypted endpoints with corporate data.
- Recovery keys stored in plaintext.
- Single-person recovery key access.
