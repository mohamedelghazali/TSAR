# MLOps Integration Guide

## Pipeline Setup
1. Isolate each stage in its own container.
2. Use workload identity (IRSA, Workload Identity, Managed Identity).
3. Hash every artifact; store hash in registry.
4. Sign models with cosign; verify before deployment.

## Registry
1. Enable access logs.
2. Enforce signed artifacts via admission policy.
3. Retain per compliance; encrypt at rest with per-tenant keys.

## Serving
1. Rate-limit per user.
2. Redact inputs/outputs for PII.
3. Enable anomaly detection on usage.

## Verification Checklist
- [ ] Every model has SBOM + AI-BOM.
- [ ] Lineage traceable to dataset and code commit.
- [ ] No raw PII in feature store or training data.
- [ ] Artifacts signed and verified.
- [ ] Serving rate-limited and isolated per tenant.
