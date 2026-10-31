# Threat Hunting

## Methodology
1. Hypothesis based on threat intel or ATT&CK gaps.
2. Data collection (EDR, SIEM, network, cloud).
3. Analysis with statistical and behavioral techniques.
4. Findings documented and shared.
5. Detection rules created from findings.

## Hypotheses
- Example: "An attacker with valid credentials would access unusual resources at unusual times."
- Example: "Lateral movement would show SMB/WinRM to non-admin hosts."

## Cadence
- Weekly hunts for Tier-1 systems.
- Monthly for broader environment.
- Ad-hoc after threat intel updates.

## Tooling
- SIEM queries saved as reusable hunts.
- Jupyter notebooks for statistical analysis.
- Threat hunting playbooks per technique.

## Forbidden
- Hunting without a hypothesis.
- Findings not converted to detections.
- Siloed hunting results.
