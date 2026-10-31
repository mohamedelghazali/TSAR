# Embedded / Firmware Security Baseline

## Boot
- Secure boot with hardware root of trust.
- Signed firmware verified at every stage.
- Anti-rollback counters.

## Crypto
- Hardware crypto accelerator or Secure Element for keys.
- Keys never in plain flash.
- Unique device identity (certificate or PUF).

## Network
- mTLS with per-device certificates.
- No default credentials; provisioning-time unique secrets.

## Updates
- Signed OTA updates with rollback protection.
- Staged rollout with health verification.

## Debug
- Debug ports (JTAG, UART) disabled or locked in production.
- Memory readout protection enabled.
