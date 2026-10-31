# Multi-Cloud Security

## Identity Federation
- One primary identity provider (Okta, Azure AD, Google Workspace).
- Short-lived tokens for cross-cloud access.
- No long-lived API keys for cross-cloud automation.

## Network
- Private interconnect or VPN between clouds; no public peering for sensitive data.
- Consistent mTLS between services across clouds.
- Per-cloud egress monitoring; aggregate at SIEM.

## Key Management
- Cross-cloud key wrapping via per-cloud KMS.
- Never export raw keys between clouds.
- Rotation schedules synchronized.

## Logging
- Unified log schema across clouds (OCSF or custom).
- Central SIEM with cross-cloud correlation.
- Retention aligned to the strictest applicable policy.

## Policy
- IaC enforced across clouds (Terraform/OpenTofu with policy-as-code).
- Same security baselines applied regardless of cloud.
- Regular cross-cloud drift detection.

## Forbidden
- Cross-cloud credentials stored in one cloud's secret manager.
- Cloud-specific bypasses of global policy.
