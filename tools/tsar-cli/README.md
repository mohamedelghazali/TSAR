# TSAR CLI

Single entry point for TSAR operations.

## Install
```bash
chmod +x tools/tsar-cli/tsar.py
ln -s "$(pwd)/tools/tsar-cli/tsar.py" /usr/local/bin/tsar
```

## Commands
| Command | Description |
|---|---|
| `tsar scan [path] [--format text\|sarif] [--output file]` | Run secret scanner and secure review. |
| `tsar inventory [path]` | Build cryptographic inventory (CBOM). |
| `tsar lint` | Validate TSAR rules and manifest. |
| `tsar version` | Compare local and remote manifest version. |
| `tsar threat-model <file>` | Generate a STRIDE threat model. |
| `tsar init [path] --agent <name>` | Bootstrap TSAR into a project. |

## Supported `--agent` values
`claude`, `claude-code`, `cursor`, `copilot`, `windsurf`, `windsurf-rc`, `generic`.

## `tsar init` behavior
1. Copies the agent-specific prompt into the correct file.
2. Vendors `.tsar/` locally for offline operation.
3. Installs a pre-commit hook if `.git/` exists.
4. Writes `.tsar/config.json` recording the manifest version.

## Exit Codes
- 0: clean.
- 1: findings that block (secrets or HIGH severity).
- 2: tooling error (missing files, invalid arguments, unknown agent).

## SARIF
```bash
tsar scan . --format sarif --output results.sarif
```
Upload to GitHub Code Scanning or any SARIF-compatible tool.
