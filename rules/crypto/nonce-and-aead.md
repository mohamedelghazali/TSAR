# Nonce and AEAD Discipline

## Nonce Rules (AES-GCM)
- 96-bit random nonce: maximum 2^32 messages per key.
- Beyond 2^32 messages: rotate the key.
- Never reuse a nonce with the same key (catastrophic confidentiality and integrity failure).

## Nonce Rules (XChaCha20-Poly1305)
- 192-bit random nonce: collision probability negligible for practical volumes.
- Still enforce a per-key message counter and rotation policy.

## Associated Data (AAD)
- Bind context to ciphertext: user ID, tenant ID, record ID, version.
- Reject ciphertext if AAD does not match expected context.

## Key Commitment
- Use AES-GCM-SIV or an explicit key-commitment construction when decrypting attacker-supplied ciphertexts under multiple keys.

## Test Vectors
Every implementation MUST be tested against NIST CAVP vectors and RFC test vectors for the chosen AEAD.
