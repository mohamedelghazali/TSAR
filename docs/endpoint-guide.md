# Endpoint Security Guide

## Baseline Requirements
| Control | Requirement |
|---|---|
| Disk encryption | FileVault, BitLocker, LUKS2, hardware FDE |
| Screen lock | <= 15 min idle, biometric or PIN >= 6 |
| Firewall | Enabled, default-deny inbound |
| EDR | Deployed, tamper-protected, reporting |
| Patching | Critical 7d, High 30d, Medium 90d |
| Application control | Gatekeeper/AppLocker/WDAC |
| MDM | Enrolled, compliance-checked |

## Verification
- MDM compliance report per device.
- EDR coverage report; alert on offline agents.
- Patch compliance report weekly.
- Encryption status continuous check.

## Incident Response
- On compromise: isolate via EDR, snapshot memory, revoke tokens, reimage after forensics.
- On lost device: remote wipe, revoke sessions, notify security.
