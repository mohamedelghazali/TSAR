# Reporting Guide

## Report Types
| Type | Frequency | Audience |
|---|---|---|
| Scan report | Per release | Engineering |
| Compliance report | Monthly | Compliance |
| Risk register | Monthly | Leadership |
| Incident report | Per incident | Security + exec |

## Generation
```bash
python tools/tsar-report/generate.py . --format html --output report.html
```

## Distribution
- Store in access-controlled location.
- Never email reports containing internal paths.
- Retain per compliance requirements.

## Contents
- Summary of findings (severity counts).
- Secret detections (locations only, never values).
- Secure review findings.
- Cryptographic inventory.
- Manifest version and timestamp.
