# Orchestrator Guide

## Purpose
Single command runs every TSAR check and emits a unified report.

## Command
```bash
tsar-orchestrator . --format markdown --output report.md
tsar-orchestrator . --format json --output report.json
```

## Steps
| Step | Tool |
|---|---|
| lint | scripts/lint_rules.py |
| secrets | skills/secret-scanner |
| review | skills/secure-review |
| cbom | skills/crypto-inventory |
| compliance | tsar-cli compliance |

## CI
The orchestrator workflow runs on every push, PR, and weekly schedule.
Artifacts uploaded for audit.

## Extending
Add a step by implementing a `step_<name>` function and registering it in
`run_pipeline`. Every step returns a `StepResult` with exit code and outputs.
