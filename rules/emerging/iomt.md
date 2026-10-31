# Internet of Medical Things (IoMT)

## Device Security
- Unique device identity (X.509 cert or PUF).
- Secure boot with hardware root of trust.
- Encrypted storage for PHI.
- No default credentials; forced rotation.

## Network
- Segment medical devices on dedicated VLAN.
- mTLS for device-to-cloud.
- No direct internet exposure.
- Traffic monitored for anomalies.

## Data
- PHI encrypted in transit and at rest.
- Access controlled per role.
- Audit logs forwarded to SIEM.
- Retention per HIPAA/FDA.

## Updates
- Signed OTA updates with anti-rollback.
- Tested on staging devices before fleet rollout.
- Rollback capability.

## Safety
- Fail-safe behavior on security events.
- No remote commands that can harm patient (safety review required).
- Coordinated disclosure with FDA per postmarket guidance.

## Decommission
- Secure wipe of PHI.
- Certificate revocation.
- Firmware reset to factory with data destruction.

## Forbidden
- Devices without unique identity.
- Unencrypted PHI at rest.
- Default passwords.
- Direct internet exposure.
- Unauthenticated OTA updates.
