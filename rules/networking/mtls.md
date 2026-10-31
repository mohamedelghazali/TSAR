# Mutual TLS (mTLS)

## Certificate Authority
- Private CA for internal services (Vault PKI, AWS Private CA, cert-manager).
- Root CA offline; intermediate CAs online with short lifetimes.
- CRL or OCSP for revocation; prefer short-lived certs (< 24 hours).

## Certificate Issuance
- Workload identity (SPIFFE ID, k8s service account) requests certificates.
- Certificates bound to workload identity in SAN.
- Short TTL: 1-24 hours for services; rotate automatically.

## Verification
- Both sides verify the peer certificate chain.
- Hostname/SAN verification mandatory; no `InsecureSkipVerify`.
- Pin the CA, not the leaf; allow rotation.
- Reject expired or revoked certificates.

## Cipher Suites
- TLS 1.3 only.
- Prefer `TLS_AES_256_GCM_SHA384` and `TLS_CHACHA20_POLY1305_SHA256`.
- Enable post-quantum hybrid (X25519MLKEM768) where supported.

## Rotation
- Automated rotation via cert-manager, Vault agent, or SPIRE.
- Zero-downtime: overlap old and new certs during rotation.
- Alert on certificates expiring within 7 days.

## Forbidden
- Long-lived service certificates (> 24 hours).
- Shared certificates across services.
- Manual certificate management in production.
- Disabled verification for "convenience".
