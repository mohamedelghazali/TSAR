# Infrastructure Security Guide

## Layers
| Layer | Controls |
|---|---|
| Hypervisor | Secure boot, TPM, encrypted migration |
| VM | Immutable, encrypted, EDR |
| Containers | Signed images, least privilege |
| Orchestration | RBAC, network policy, workload identity |

## Verification
- [ ] Host firmware signed and measured.
- [ ] Live migration encrypted.
- [ ] Volumes encrypted with per-tenant keys.
- [ ] Orchestrator uses mTLS internally.
- [ ] Admission control verifies image signatures.
- [ ] Resource limits enforced.
