# Secure SDLC

## Phases
| Phase | Security Activities |
|---|---|
| Requirements | Security requirements, abuse cases, compliance mapping |
| Design | Threat model, architecture review, privacy impact assessment |
| Implementation | Secure coding rules (TSAR), pair review, static analysis |
| Testing | SAST, DAST, fuzzing, penetration, chaos |
| Deployment | Signed artifacts, SBOM, admission control |
| Operations | Monitoring, patch management, incident response |
| Decommission | Data deletion, key destruction, archival |

## Gates
- Design gate: threat model approved.
- Code gate: SAST/SCA/secrets clean.
- Test gate: DAST clean, penetration signed off.
- Release gate: signed artifacts, SBOM, provenance.
- Deploy gate: admission policy verifies.

## Requirements
- Security requirements for every Tier-1 feature.
- Abuse cases documented alongside use cases.
- Compliance requirements traced to controls.
- Risk register updated.

## Metrics
- Time to remediate per severity.
- Vulnerability density.
- Test coverage on security-critical paths.
- Detection coverage.

## Forbidden
- Skipping gates for speed.
- Deployments without threat model for Tier-1.
- Release without SBOM.
