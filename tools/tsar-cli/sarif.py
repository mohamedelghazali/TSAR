"""SARIF 2.1.0 emitter for TSAR findings."""
import json
from pathlib import Path

CWE_MAP = {
    "sql_injection": "CWE-89",
    "command_injection": "CWE-78",
    "eval_usage": "CWE-95",
    "pickle_load": "CWE-502",
    "innerhtml": "CWE-79",
    "dangerous_html": "CWE-79",
    "ssrf": "CWE-918",
    "path_traversal": "CWE-22",
    "tls_disabled": "CWE-295",
    "weak_crypto": "CWE-327",
    "weak_random": "CWE-338",
    "aws_key": "CWE-798",
    "openai_key": "CWE-798",
    "github_token": "CWE-798",
    "private_key": "CWE-798",
    "high_entropy": "CWE-798",
}

def emit(findings, out_path: Path):
    rules = {}
    results = []
    for f, line, kind, sev, hint in findings:
        cwe = CWE_MAP.get(kind, "CWE-693")
        rule_id = f"tsar/{kind}"
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": kind,
                "shortDescription": {"text": hint},
                "properties": {"tags": [cwe, "security"]},
            }
        results.append({
            "ruleId": rule_id,
            "level": "error" if sev == "HIGH" else "warning",
            "message": {"text": hint},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": str(f)},
                    "region": {"startLine": line},
                }
            }],
        })
    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "TSAR",
                "version": "1.0.0",
                "rules": list(rules.values()),
            }},
            "results": results,
        }],
    }
    out_path.write_text(json.dumps(sarif, indent=2))
