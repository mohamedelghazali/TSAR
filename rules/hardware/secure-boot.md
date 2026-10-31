# Secure Boot Chain

## Chain of Trust
Root of Trust (immutable) -> Bootloader (signed) -> OS kernel (signed) -> Userspace (verified).

## Requirements
- Each stage verifies the next before execution.
- Rollback counters prevent downgrade to vulnerable versions.
- Recovery mode requires physical presence or signed recovery image.

## Measurement
- PCR measurements logged and attestable.
- Baseline stored outside the device.
