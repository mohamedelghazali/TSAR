#!/usr/bin/env python3
"""TSAR report generator: HTML and PDF from scanner output."""
import argparse
import datetime
import json
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

def run_scanner(script: Path, target: str) -> str:
    try:
        r = subprocess.run([sys.executable, str(script), target],
                           capture_output=True, text=True, timeout=600)
        return r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"

def read_manifest_version() -> str:
    import yaml
    data = yaml.safe_load((ROOT / "manifest.yaml").read_text())
    return data.get("version", "unknown")

def parse_secrets(output: str) -> list[dict]:
    rows = []
    for line in output.splitlines():
        if line.startswith("BLOCK:"):
            parts = line[len("BLOCK:"):].strip().split()
            if len(parts) >= 2:
                location = parts[0]
                kind = parts[1].strip("[]")
                rows.append({"location": location, "kind": kind})
    return rows

def parse_review(output: str) -> list[dict]:
    rows = []
    for line in output.splitlines():
        for sev in ("HIGH", "MEDIUM", "LOW"):
            if line.startswith(f"{sev}:"):
                rest = line[len(sev) + 1:].strip()
                parts = rest.split(" ", 1)
                if len(parts) == 2:
                    location = parts[0]
                    detail = parts[1]
                    rows.append({"severity": sev, "location": location, "detail": detail})
    return rows

def parse_cbom(output: str) -> dict:
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {}

def render_table(rows: list[dict], columns: list[str]) -> str:
    if not rows:
        return "<p>None.</p>"
    head = "".join(f"<th>{c}</th>" for c in columns)
    body = ""
    for row in rows:
        cells = ""
        for c in columns:
            value = row.get(c.lower(), "")
            cls = ""
            if c.lower() == "severity":
                cls = f' class="sev-{value.lower()}"'
            cells += f"<td{cls}>{value}</td>"
        body += f"<tr>{cells}</tr>"
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

def render_cbom(cbom: dict) -> str:
    algos = cbom.get("algorithms", {})
    if not algos:
        return "<p>No algorithms detected.</p>"
    rows = []
    for name, info in algos.items():
        rows.append({
            "algorithm": name,
            "count": str(info.get("count", 0)),
            "risky": "yes" if name in cbom.get("risky", []) else "no",
        })
    return render_table(rows, ["Algorithm", "Count", "Risky"])

def generate_html(target: str) -> str:
    secrets_out = run_scanner(SKILLS / "secret-scanner" / "scanner.py", target)
    review_out = run_scanner(SKILLS / "secure-review" / "review.py", target)
    cbom_out = run_scanner(SKILLS / "crypto-inventory" / "inventory.py", target)

    secrets = parse_secrets(secrets_out)
    review = parse_review(review_out)
    cbom = parse_cbom(cbom_out)

    counts = {sev: sum(1 for r in review if r["severity"] == sev)
              for sev in ("HIGH", "MEDIUM", "LOW")}

    return HTML_TEMPLATE.format(
        generated=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        manifest_version=read_manifest_version(),
        target=target,
        high=counts["HIGH"], medium=counts["MEDIUM"], low=counts["LOW"],
        secrets=len(secrets),
        secrets_table=render_table(secrets, ["Location", "Kind"]),
        review_table=render_table(review, ["Severity", "Location", "Detail"]),
        cbom_table=render_cbom(cbom),
    )

def main() -> int:
    p = argparse.ArgumentParser(description="Generate TSAR security report")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--format", choices=["html", "json"], default="html")
    p.add_argument("--output", default="tsar-report.html")
    args = p.parse_args()

    if args.format == "html":
        html = generate_html(args.path)
        Path(args.output).write_text(html)
        print(f"Report written to {args.output}")
        return 0

    report = {
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "manifest_version": read_manifest_version(),
        "target": args.path,
        "secrets": parse_secrets(run_scanner(SKILLS / "secret-scanner" / "scanner.py", args.path)),
        "review": parse_review(run_scanner(SKILLS / "secure-review" / "review.py", args.path)),
        "cbom": parse_cbom(run_scanner(SKILLS / "crypto-inventory" / "inventory.py", args.path)),
    }
    Path(args.output).write_text(json.dumps(report, indent=2))
    print(f"Report written to {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
