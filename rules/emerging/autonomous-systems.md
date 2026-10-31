# Autonomous Systems (Vehicles, Drones, Robotics)

## Safety-Critical Isolation
- Safety controller isolated from autonomy stack.
- No remote override that can be blocked by autonomy software.
- Deterministic real-time control separate from ML inference.

## Perception and Decision
- Sensor spoofing detection.
- Model robustness testing (adversarial inputs).
- Fallback to safe state on uncertainty.
- Logging of decisions for post-incident analysis.

## Communications
- mTLS for V2X and cloud links.
- Command authenticity verification.
- Replay protection (nonce, timestamp, sequence).
- No unauthenticated remote commands.

## Updates
- Signed firmware with anti-rollback.
- Staged rollout with safety validation.
- Over-the-air updates only with explicit safety case.

## Physical Security
- Tamper detection on critical components.
- Secure boot with measured boot.
- Hardware security module for keys.

## Incident Response
- Remote kill switch with multi-party authentication.
- Forensic capture without disabling safety systems.
- Coordination with regulators.

## Forbidden
- ML-driven control without deterministic safety layer.
- Unauthenticated remote commands.
- OTA updates without rollback.
- Autonomy stack with filesystem access to safety controller.
