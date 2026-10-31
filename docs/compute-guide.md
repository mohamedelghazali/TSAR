# Compute Security Guide

## Serverless
- Per-function IAM; no wildcards.
- Secrets via manager at runtime.
- Schema validation on every event.
- VPC attachment for private resources.
- SBOM + signing per bundle.

## Confidential Computing
- Use for multi-tenant or third-party data.
- Verify attestation before releasing keys.
- Combine with defense-in-depth; TEEs are not sufficient alone.

## VMs and Bare Metal
- Immutable images; no in-place patching.
- Instance identity (IMDSv2, metadata tokens).
- OS hardening baseline (CIS).
- Patch within SLA (critical: 7 days, high: 30 days).

## Verification
- [ ] Least-privilege IAM.
- [ ] No secrets in env.
- [ ] Input validated.
- [ ] Network egress restricted.
- [ ] Attestation verified (if TEE).
