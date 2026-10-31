# TSAR Orchestrator

Runs all TSAR checks in a single pipeline and emits unified reports.

## Steps
- `lint`: validate TSAR rules and manifest.
- `secrets`: scan for hardcoded secrets.
- `review`: static security review.
- `cbom`: cryptographic inventory.
- `compliance`: verify compliance mapping references (soc2, iso27001, pci-dss, hipaa, gdpr).

## Usage
```bash
python tools/tsar-orchestrator/orchestrator.py . --format markdown --output tsar-orchestrator.md
python tools/tsar-orchestrator/orchestrator.py . --format json --output tsar-orchestrator.json
```

## CI Integration
```yaml
- name: TSAR orchestrator
  run: |
    python tools/tsar-orchestrator/orchestrator.py . \
      --format markdown \
      --output tsar-orchestrator.md
- uses: actions/upload-artifact@c2acdedd35a8824a1552c7137f8c18288c3ea469
  with:
    name: tsar-orchestrator
    path: tsar-orchestrator.md
```

## Exit Codes
- 0: all steps passed.
- 1: at least one step failed.
- 2: tooling error.

## Design
- Deterministic: same inputs produce same outputs.
- No network calls except compliance fetch (optional).
- No side effects on the target project.
- JSON output machine-parseable for downstream tooling.
