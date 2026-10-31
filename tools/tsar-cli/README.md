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
| `tsar scan [path]` | Run secret scanner and secure review. |
| `tsar inventory [path]` | Build cryptographic inventory (CBOM). |
| `tsar lint` | Validate TSAR rules and manifest. |
| `tsar version` | Compare local and remote manifest version. |
| `tsar threat-model <file>` | Generate a STRIDE threat model. |

## Exit Codes
- 0: clean.
- 1: findings that block (secrets or HIGH severity).
- 2: tooling error (missing files, network failure).
