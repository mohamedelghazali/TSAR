# Application Control

## Allow-listing
- Default-deny for executables on high-value endpoints.
- Allow-list signed by trusted publishers.
- Update process for new applications documented.

## macOS
- Gatekeeper enforced; no unsigned apps.
- Notarization required for distribution.

## Windows
- AppLocker or WDAC enforced.
- SmartScreen enabled.
- Block macros from internet-originated documents.

## Linux
- Package manager restrictions; no compilation on production.
- SELinux/AppArmor enforcing.

## Blocking
- Block known-bad hashes via EDR.
- Block execution from user-writable directories (`/tmp`, `%TEMP%`).
- Block unsigned binaries.

## Forbidden
- Disabled Gatekeeper/SmartScreen.
- Executables running from user-writable paths.
- Unvetted applications on production endpoints.
