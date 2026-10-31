# Cryptographic Algorithm Selection (2026 Baseline)

## 1. Symmetric Encryption (AEAD)
| Use Case | Mandatory | Forbidden |
|---|---|---|
| General data at rest | AES-256-GCM | ECB, CBC without MAC, RC4, DES/3DES, AES-CTR alone |
| Random-nonce safety | XChaCha20-Poly1305 (192-bit nonce) | AES-GCM with random 96-bit nonce beyond 2^32 messages |
| Nonce-misuse resistance | AES-GCM-SIV | Caller-managed nonce discipline |
| Large payloads (> few MB) | Chunked XChaCha20-Poly1305 with per-chunk AAD | Single-pass AEAD over unbounded data |
| Key wrapping | AES-256-KW (RFC 3394) | Raw key bytes in transit |

## 2. Password Hashing
| Algorithm | Parameters | Status |
|---|---|---|
| Argon2id | m=65536 KiB, t=3, p=4, salt=16B | REQUIRED |
| scrypt | N=2^17, r=8, p=1 | ACCEPTABLE |
| bcrypt | cost >= 12 | LEGACY — migrate to Argon2id |
| PBKDF2-HMAC-SHA256 | iterations >= 600,000 | FIPS-only |
| SHA-256/512 alone | — | FORBIDDEN (CWE-916) |

## 3. Key Exchange & Asymmetric
| Purpose | Mandatory | Migration Deadline |
|---|---|---|
| Key exchange | X25519 + ML-KEM-768 hybrid (FIPS 203) | New code immediately |
| Signatures | Ed25519; ML-DSA-44 (FIPS 204) for PQ | Dual-sign during transition |
| Asymmetric encryption | HPKE (MLKEM768-X25519, HKDF-SHA256, AES-128-GCM) | — |
| RSA | RSA-2048 min, OAEP only | Disallowed for new code after 2030 |
| ECDSA | P-256 min | Disallowed for new code after 2030 |

## 4. Hashing & MAC
| Purpose | Mandatory | Forbidden |
|---|---|---|
| Integrity | SHA-256, SHA-512, BLAKE2, BLAKE3 | MD5, SHA-1 |
| MAC | HMAC-SHA-256, KMAC | H(key||msg) — length extension |
| KDF | HKDF with per-purpose `info` labels | Raw hash of key material |
| Password storage | Argon2id | Any fast hash |

## 5. Randomness
| Purpose | Requirement |
|---|---|
| Tokens / nonces | CSPRNG, >=32 bytes (`getrandom`, `SecRandomCopyBytes`, `SecureRandom`, `crypto.randomBytes`) |
| Seeds | OS CSPRNG only |
| Forbidden | `Math.random()`, `rand()`, `time()` seeds, UUIDv1 for security |

## 6. TLS
| Requirement | Value |
|---|---|
| Version | TLS 1.3 only (TLS 1.2 legacy only with approved suites) |
| Cipher suites | `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256` |
| Certificate verification | Mandatory; no exceptions |
| HSTS | `max-age>=31536000; includeSubDomains; preload` |
| Pinning | Required for Tier-1 mobile and high-value APIs |
