# Threat Intelligence Guide

## Pipeline
1. Collect (STIX/TAXII feeds, commercial, OSINT).
2. Validate (schema, freshness, confidence).
3. Enrich (asset context, exposure).
4. Publish (SIEM, EDR, WAF, DNS).
5. Measure (precision, MTTD).
6. Retire (expiry, false positives).

## Standards
- STIX 2.1 for sharing.
- TAXII 2.1 for transport.
- MITRE ATT&CK for technique mapping.
- TLP for handling markings.

## Detection Lifecycle
- New detection -> test -> deploy -> tune -> review -> retire.
- Every detection has runbook + ATT&CK mapping + owner.
