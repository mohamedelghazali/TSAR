# Mobile Device Management (MDM)

## Enrollment
- Automated enrollment for corporate devices.
- BYOD with containerization (work profile on Android, managed apps on iOS).
- Enrollment tied to identity (SSO + MFA).

## Compliance
- OS version minimum enforced.
- Disk encryption required (FileVault, BitLocker, Android/iOS FDE).
- Screen lock required (biometric or PIN >= 6 digits).
- Jailbreak/root detection enabled.
- Anti-malware installed and updated.

## Policies
- Remote wipe for lost/stolen devices.
- Selective wipe for BYOD (work container only).
- App allow-list/block-list.
- Network access via per-app VPN.

## Privacy
- BYOD: no access to personal data; visible only work container.
- Clear privacy notice at enrollment.
- User consent for location tracking (only on managed devices for security).

## Forbidden
- Unmanaged devices accessing corporate email or apps.
- Bypassing compliance checks.
- Accessing personal data on BYOD.
