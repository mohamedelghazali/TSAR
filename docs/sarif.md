# SARIF Output

`tsar scan` can emit SARIF 2.1.0 for GitHub Code Scanning.

## Usage
```bash
python tools/tsar-cli/tsar.py scan . --format sarif > results.sarif
```

## Integration
```yaml
permissions:
  contents: read
  security-events: write
- name: TSAR scan (SARIF)
  run: python tools/tsar-cli/tsar.py scan . --format sarif > results.sarif
- uses: github/codeql-action/upload-sarif@9b3254085494b55a0f7c4c2b3d2d52cc712ce370
  with:
    sarif_file: results.sarif
```

## Mapping
- `sql_injection` → CWE-89
- `command_injection` → CWE-78
- `eval_usage` → CWE-95
- `pickle_load` → CWE-502
- `innerhtml` → CWE-79
- `ssrf` → CWE-918
- `path_traversal` → CWE-22
- `tls_disabled` → CWE-295
- `weak_crypto` → CWE-327
- `weak_random` → CWE-338
- `hardcoded_secret` → CWE-798
