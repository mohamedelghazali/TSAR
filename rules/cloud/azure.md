# Azure Security Baseline

## Identity
- Managed Identities for workloads; no client secrets where possible.
- Conditional Access enforced for all human users.
- PIM (Privileged Identity Management) for admin roles; just-in-time activation.
- No standing Global Administrator assignments.

## Networking
- Hub-and-spoke with Azure Firewall or NVA.
- Network Security Groups: deny by default; explicit allow.
- Private Endpoints for PaaS services.
- DDoS Protection Standard for public-facing workloads.

## Compute
- VMs: Trusted Launch (Secure Boot, vTPM), disk encryption with CMK.
- AKS: Azure AD integration, Workload Identity, private cluster, network policies.
- App Service: managed identity, private endpoints, TLS 1.3.

## Storage
- Storage Accounts: `allowBlobPublicAccess: false`, `minimumTlsVersion: TLS1_2` (or 1.3), `supportsHttpsTrafficOnly: true`.
- Encryption with customer-managed keys for sensitive data.
- Immutable blob storage for audit and compliance.

## Logging
- Azure Monitor + Log Analytics workspace with retention per policy.
- Microsoft Defender for Cloud enabled on all subscriptions.
- Diagnostic settings forwarded for all control-plane and data-plane operations.

## Key Vault
- RBAC authorization (not legacy access policies).
- Soft-delete and purge protection enabled.
- Private endpoint access only.
- Key rotation policies for all keys.

## Secrets
- Key Vault references in App Service, AKS, and Functions.
- No secrets in ARM templates or pipeline variables without Key Vault linkage.

## Forbidden
- Storage accounts with public blob access.
- AKS clusters without private API server.
- Subscription-level Owner for workloads.
- Unencrypted managed disks.
