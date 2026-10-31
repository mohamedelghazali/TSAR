# TSAR Report Generator

Aggregates secret scan, secure review, and crypto inventory into a single
HTML or JSON report.

## Usage
```bash
python tools/tsar-report/generate.py . --format html --output report.html
python tools/tsar-report/generate.py . --format json --output report.json
```

## Contents
- Secrets detected (with locations, no values).
- Secure review findings grouped by severity.
- Cryptographic inventory (CBOM) with risky algorithms flagged.
- Manifest version and generation timestamp.

## Security
- The report contains file paths and pattern names, never secrets or PII.
- Reports should be stored in access-controlled storage.
- Do not publish reports containing internal paths.

## CI Integration
```yaml
- name: TSAR report
  run: python tools/tsar-report/generate.py . --output tsar-report.html
- uses: actions/upload-artifact@c2acdedd35a8824a1552c7137f8c18288c3ea469
  with:
    name: tsar-report
    path: tsar-report.html
```
