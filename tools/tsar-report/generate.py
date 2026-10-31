#!/usr/bin/env python3
"""TSAR report generator: escaped HTML and structured JSON from scanner output."""
import argparse
import datetime
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS = ROOT / "skills"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>TSAR Security Report</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 40px; color: #1a1a1a; }
h1 { border-bottom: 2px solid #333; padding-bottom: 8px; }
h2 { margin-top: 40px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
table { border-collapse: collapse; width: 100%; margin-top: 12px; }
th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 13px; }
th { background: #f4f4f4; }
.sev-high { color: #b00020; font-weight: 600; }
.sev-medium { color: #b36b00; }
.sev-low { color: #33691e; }
.meta { color: #666; font-size: 12px; }
.summary { background: #f9f9f9; padding: 12px; border-left: 4px solid #333; margin: 16px 0; }
</style>
</head>
<body>
<h1>TSAR Security Report</h1>
<p class="meta">Generated: {generated} &middot; Manifest version: {manifest_version} &middot; Target: {target}</p>
<p class="meta">Scanner execution: {scanner_status}</p>
<div class="summary">
<strong>Summary:</strong> {high} high, {medium} medium, {low} low findings, {secrets} secrets detected.
</div>
<h2>Secrets</h2>
{secrets_table}
<h2>Secure Review Findings</h2>
{review_table}
<h2>Crypto Inventory (CBOM)</h2>
{cbom_table}
</body>
</html>
"""

def run_scanner(script: Path, target: str) -> tuple[str, int]:
    try:
        result = subprocess.run(
            [sys.executable, str(script), target],
            capture_output=True, text=True, timeout=600, check=False,
        )
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "ERROR: scanner timed out after 600 seconds", 124
    except OSError as exc:
        return f"ERROR: unable to execute scanner: {exc}", 127

def read_manifest_version() -> str:
    import yaml
    data = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    return str(data.get("version", "unknown"))

def parse_secrets(output: str) -> list[dict]:
    rows = []
    pattern = re.compile(r"^BLOCK:\s+(.*):(\d+)\s+\[([^]]+)\]\s*$")
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            rows.append({"location": f"{match.group(1)}:{match.group(2)}", "kind": match.group(3)})
    return rows

def parse_review(output: str) -> list[dict]:
    rows = []
    pattern = re.compile(r"^(HIGH|MEDIUM|LOW):\s+(.*):(\d+)\s+\[([^]]+)\]\s*(.*)$")
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            rows.append({
                "severity": match.group(1),
                "location": f"{match.group(2)}:{match.group(3)}",
                "kind": match.group(4),
                "detail": match.group(5),
            })
    return rows

def parse_cbom(output: str) -> dict:
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {}

def render_table(rows: list[dict], columns: list[str]) -> str:
    if not rows:
        return "<p>None.</p>"
    head = "".join(f"<th>{html.escape(column, quote=True)}</th>" for column in columns)
    body = []
    for row in rows:
        cells = []
        for column in columns:
            value = str(row.get(column.lower(), ""))
            cls = ""
            if column.lower() == "severity":
                severity = value.lower()
                if severity in {"high", "medium", "low"}:
                    cls = f' class="sev-{severity}"'
            cells.append(f"<td{cls}>{html.escape(value, quote=True)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return "<table><thead><tr>" + head + "</tr></thead><tbody>" + "".join(body) + "</tbody></table>"

def render_cbom(cbom: dict) -> str:
    algorithms = cbom.get("algorithms", {})
    if not algorithms:
        return "<p>No algorithms detected.</p>"
    rows = [
        {
            "algorithm": str(name),
            "count": str(info.get("count", 0)),
            "risky": "yes" if name in cbom.get("risky", []) else "no",
        }
        for name, info in algorithms.items()
    ]
    return render_table(rows, ["Algorithm", "Count", "Risky"])

def _status_label(code: int) -> str:
    if code == 0:
        return "completed"
    if code == 1:
        return "completed_with_findings"
    return f"execution_error_{code}"

def collect(target: str) -> dict:
    secret_output, secret_rc = run_scanner(SKILLS / "secret-scanner" / "scanner.py", target)
    review_output, review_rc = run_scanner(SKILLS / "secure-review" / "review.py", target)
    cbom_output, cbom_rc = run_scanner(SKILLS / "crypto-inventory" / "inventory.py", target)
    return {
        "secrets": parse_secrets(secret_output),
        "review": parse_review(review_output),
        "cbom": parse_cbom(cbom_output),
        "scanner_status": {
            "secret_scanner": _status_label(secret_rc),
            "secure_review": _status_label(review_rc),
            "crypto_inventory": _status_label(cbom_rc),
        },
        "scanner_output": {
            "secret_scanner": secret_output,
            "secure_review": review_output,
            "crypto_inventory": cbom_output,
        },
        "scanner_exit_codes": {
            "secret_scanner": secret_rc,
            "secure_review": review_rc,
            "crypto_inventory": cbom_rc,
        },
    }

def generate_html(target: str, data: dict | None = None) -> str:
    data = data if data is not None else collect(target)
    review = data["review"]
    counts = {severity: sum(1 for row in review if row["severity"] == severity)
              for severity in ("HIGH", "MEDIUM", "LOW")}
    values = {
        "generated": html.escape(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), quote=True),
        "manifest_version": html.escape(read_manifest_version(), quote=True),
        "target": html.escape(str(target), quote=True),
        "scanner_status": html.escape(json.dumps(data["scanner_status"], sort_keys=True), quote=True),
        "high": counts["HIGH"], "medium": counts["MEDIUM"], "low": counts["LOW"],
        "secrets": len(data["secrets"]),
        "secrets_table": render_table(data["secrets"], ["Location", "Kind"]),
        "review_table": render_table(review, ["Severity", "Location", "Kind", "Detail"]),
        "cbom_table": render_cbom(data["cbom"]),
    }
    rendered = HTML_TEMPLATE
    for key, value in values.items():
        rendered = rendered.replace("{" + key + "}", str(value))
    return rendered

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate TSAR security report")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--format", choices=["html", "json"], default="html")
    parser.add_argument("--output", default="tsar-report.html")
    args = parser.parse_args()

    data = collect(args.path)
    report = {
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "manifest_version": read_manifest_version(),
        "target": args.path,
        "secrets": data["secrets"],
        "review": data["review"],
        "cbom": data["cbom"],
        "scanner_status": data["scanner_status"],
        "scanner_exit_codes": data["scanner_exit_codes"],
        "scanner_output": data["scanner_output"],
    }
    if args.format == "html":
        output = generate_html(args.path, data)
    else:
        output = json.dumps(report, indent=2)
    Path(args.output).write_text(output, encoding="utf-8")
    print(f"Report written to {args.output}")
    # Findings are reportable; only scanner execution errors produce a non-zero report status.
    return 2 if any(code not in (0, 1) for code in data["scanner_exit_codes"].values()) else 0

if __name__ == "__main__":
    raise SystemExit(main())
