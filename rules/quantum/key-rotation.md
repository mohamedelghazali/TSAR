# Key Rotation for Post-Quantum Migration

## Principles
- Every key has a version and an algorithm identifier.
- Rotation does not require redeployment; keys are loaded per-session.
- Old keys remain for decryption only, never encryption.

## Rotation Triggers
| Event | Action |
|---|---|
| Algorithm deprecation | Rotate to new algorithm |
| Annual review | Rotate KEKs |
| Suspected compromise | Immediate rotate + re-encrypt |
| 2^32 messages on a DEK | Rotate DEK |
| Employee exit | Rotate accessed keys |

## Storage
- Store `(key_version, algorithm_id, ciphertext)` tuples.
- Decrypt using the version indicated in the tuple.
- Never assume current key is the encryption key for old ciphertexts.

## Migration Path
1. Support classical + hybrid decryption.
2. New writes use hybrid.
3. Re-encrypt high-value data to hybrid over time.
4. Retire classical-only decryption after 2030.
