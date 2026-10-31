# Desktop Application Security

## Storage
- Windows: DPAPI for secrets, Credential Manager for user credentials.
- macOS: Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`.
- Linux: Secret Service API (libsecret) or KWallet.
- Never in plaintext config files, registry keys, or plists.

## Auto-Update
- Signed updates (Authenticode on Windows, Developer ID on macOS, GPG on Linux).
- Verify signature before installation.
- TLS for update delivery with certificate pinning.
- Rollback protection: version counters.

## Sandboxing
- macOS: App Sandbox with minimal entitlements.
- Windows: AppContainer where feasible.
- Linux: Flatpak/Snap sandbox with portal APIs.

## Process Hardening
- ASLR, DEP, stack canaries enabled.
- Control Flow Integrity where supported.
- Seccomp on Linux for syscall filtering.
- No world-writable paths for temp files.

## Network
- TLS 1.3 with verification.
- Certificate pinning for high-value APIs.
- Proxy support without disabling verification.

## IPC
- Named pipes/local sockets with authentication.
- Verify peer identity (ACL, SO_PEERCRED).
- No unauthenticated D-Bus interfaces.

## Forbidden
- Unsigned binaries.
- Disabled code signing verification.
- Secrets in binary strings.
- Debug interfaces in production.
- Loading plugins from user-writable directories.
