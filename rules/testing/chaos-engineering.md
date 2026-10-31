# Chaos Engineering

## Purpose
Validate security controls and resilience under failure, not just availability.

## Security-Focused Experiments
- Kill a service: does mTLS fail closed?
- Revoke a certificate: does the system reject?
- Block egress: does the app degrade safely?
- Inject latency into auth: does the app fail closed?
- Corrupt a secret: does the app refuse to start?

## Guardrails
- Experiments in staging first.
- Blast radius limited (single AZ, single service).
- Automatic rollback on unintended impact.
- Notify stakeholders before running.

## Tools
- Chaos Mesh, LitmusChaos, Gremlin, AWS Fault Injection Simulator.
- Custom scripts for security-specific scenarios.

## Documentation
- Experiment hypothesis.
- Steady-state metrics.
- Expected vs. observed behavior.
- Findings and remediation.

## Forbidden
- Unplanned chaos in production.
- Experiments without rollback.
- Ignoring security findings from chaos experiments.
