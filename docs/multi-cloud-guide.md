# Multi-Cloud Guide

## Identity Federation
- One primary IdP for humans.
- OIDC federation for workloads across clouds.
- No static keys between clouds.
- Short-lived tokens (<= 1 hour).

## Network
- Private interconnect or VPN.
- Consistent mTLS between services.
- Central egress monitoring.

## Key Management
- Per-cloud KMS; no key export.
- Cross-cloud encryption via wrapping.
- Rotation synchronized.

## Logging
- Unified schema across clouds.
- Central SIEM.
- Retention aligned to the strictest policy.

## Policy
- Same IaC patterns for all clouds.
- Cross-cloud drift detection.
- Consistent tagging.
