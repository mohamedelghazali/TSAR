---
name: threat-modeler
description: Create STRIDE threat models from system architectures, data flows, assets, trust boundaries, actors, and privileges. Use when designing systems, reviewing architecture, assessing attack surfaces, or planning security mitigations.
---

# Threat Modeler Skill

## Purpose
Generate a STRIDE threat model for a given system description.

## Invocation
`python skills/threat-modeler/model.py <description.txt>`

## Output
- Assets inventory.
- Trust boundaries.
- STRIDE threats per component.
- Mitigations mapped to TSAR rules.

## Required Inputs
- Architecture diagram or textual description.
- Data flows.
- Actors and privileges.
