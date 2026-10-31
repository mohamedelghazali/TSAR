# Mobile Application Security (iOS + Android)

## Storage
- iOS: Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`.
- Android: `EncryptedSharedPreferences` or Keystore-backed encryption.
- Never in plaintext files, `UserDefaults`, `SharedPreferences`.
- Biometric-gated for high-value secrets.

## Transport
- TLS 1.3 only with certificate verification.
- Certificate pinning via `NSURLSession` delegate (iOS) and `network_security_config.xml` (Android).
- Backups of pinned certs for rotation.
- Reject cleartext; `NSAllowsArbitraryLoads=false`, `cleartextTrafficPermitted=false`.

## Authentication
- OAuth 2.1 with PKCE; no client secrets in app.
- Biometric binding for sensitive actions.
- Session tokens in memory or Keychain; never in files.
- Logout clears all local state.

## Code Protection
- R8/ProGuard (Android) and bitcode/optimization (iOS) with obfuscation.
- Root/jailbreak detection for Tier-1 apps.
- Tamper detection; verify app signature at runtime.
- Anti-debug for sensitive flows.

## Dependencies
- Pin versions; scan for CVEs in CI.
- Minimal permissions; request at use time.
- No unnecessary SDKs; audit telemetry.

## Privacy
- Privacy manifest (iOS) and Data Safety (Android).
- No PII in logs or analytics.
- User consent for tracking (ATT on iOS, App Tracking Transparency).

## Deep Links
- Validate URL schemes; reject unauthorized hosts.
- App Links (Android) and Universal Links (iOS) for trusted domains.
- No sensitive data in deep link URLs.

## Forbidden
- HTTP endpoints.
- Secrets in code, resources, or build config.
- Disabled certificate validation.
- Debug builds in production.
- WebView without JS bridge restrictions.
