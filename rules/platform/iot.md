# IoT Device Security

## Identity
- Unique per-device credentials provisioned at manufacturing.
- X.509 certificate or hardware-backed key (Secure Element, TPM, PUF).
- No shared credentials across devices.

## Communication
- mTLS for all device-to-cloud traffic.
- Certificate rotation without device recall.
- No plaintext protocols (MQTT without TLS forbidden).

## Firmware
- Secure boot with hardware root of trust (see rules/hardware/secure-boot.md).
- Signed OTA updates with anti-rollback.
- Minimal attack surface; remove unused services.

## Physical
- Debug ports disabled in production.
- Tamper detection on Tier-1 devices.
- Memory readout protection enabled.

## Lifecycle
- End-of-life policy communicated; no abandoned devices.
- Vulnerability disclosure channel maintained.
