#!/bin/bash
# TSAR — Full verification script.
# Runs every security and consistency check before a release or merge to main.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

step() {
  echo ""
  echo "================================================================"
  echo "  $1"
  echo "================================================================"
}

check() {
  local name="$1"
  shift
  if "$@"; then
    echo -e "${GREEN}PASS${NC}: $name"
  else
    echo -e "${RED}FAIL${NC}: $name"
    FAILED=$((FAILED + 1))
  fi
}

step "1. Python environment"
python3 --version
if python3 -c "import yaml, pytest" >/dev/null 2>&1; then
  echo -e "${GREEN}PASS${NC}: python_dependencies"
else
  echo -e "${RED}FAIL${NC}: python_dependencies"
  echo "Install the declared development dependencies with: python3 -m pip install -r requirements-dev.txt"
  FAILED=$((FAILED + 1))
fi

step "2. Lint TSAR rules"
check "lint_rules" python3 scripts/lint_rules.py

step "3. Manifest integrity"
check "manifest_files_exist" python3 - <<'PY'
import sys, yaml
from pathlib import Path
data = yaml.safe_load(Path("manifest.yaml").read_text())
missing = []
for group, files in data["active_files"].items():
    for rel in files:
        if not Path(rel).exists():
            missing.append(rel)
if missing:
    print("Missing files:")
    for m in missing:
        print(f"  - {m}")
    sys.exit(1)
print(f"All {sum(len(v) for v in data['active_files'].values())} active files present")
PY

step "3b. No empty files"
check "no_empty_files" python3 scripts/check-no-empty-files.py

step "4. Secret scanner on repository"
check "secret_scan_repo" python3 skills/secret-scanner/scanner.py .

step "5. Secure review on secure examples"
check "secure_examples_clean" python3 skills/secure-review/review.py examples/secure

step "6. Secure review on anti-patterns (must fail)"
if python3 skills/secure-review/review.py examples/anti-patterns >/dev/null 2>&1; then
  echo -e "${RED}FAIL${NC}: anti-patterns should trigger findings"
  FAILED=$((FAILED + 1))
else
  echo -e "${GREEN}PASS${NC}: anti-patterns correctly flagged"
fi

step "7. Crypto inventory"
check "crypto_inventory" python3 skills/crypto-inventory/inventory.py examples/secure

step "8. Compliance references"
for fw in soc2 iso27001 pci-dss hipaa gdpr; do
  check "compliance_$fw" python3 tools/tsar-cli/tsar.py compliance "$fw"
done

step "9. Full test suite"
check "pytest" python3 -m pytest tests/ -q

step "10. Orchestrator on repository"
check "orchestrator" python3 tools/tsar-orchestrator/orchestrator.py examples/secure --format json --output /tmp/tsar-orch.json

step "11. Report generation"
check "report_generation" python3 tools/tsar-report/generate.py examples/secure --format json --output /tmp/tsar-report.json

step "12. OPA policies (if opa installed)"
if command -v opa >/dev/null 2>&1; then
  check "opa_check" opa check policies/
else
  echo -e "${YELLOW}SKIP${NC}: opa not installed"
fi

step "13. LSP build (if node installed)"
if command -v node >/dev/null 2>&1; then
  rm -f tools/tsar-lsp/out/server.js
  if (cd tools/tsar-lsp && npm install --silent && npm run build --silent >/dev/null 2>&1) && [ -f tools/tsar-lsp/out/server.js ]; then
    echo -e "${GREEN}PASS${NC}: lsp_build"
  else
    echo -e "${RED}FAIL${NC}: lsp_build"
    FAILED=$((FAILED + 1))
  fi
else
  echo -e "${YELLOW}SKIP${NC}: node not installed"
fi

step "14. Terraform validation (if terraform installed)"
if command -v terraform >/dev/null 2>&1; then
  if (cd examples/secure/terraform && terraform init -backend=false >/dev/null 2>&1); then
    check "terraform_validate" bash -c 'cd examples/secure/terraform && terraform validate'
  else
    echo -e "${RED}FAIL${NC}: terraform_init"
    FAILED=$((FAILED + 1))
  fi
else
  echo -e "${YELLOW}SKIP${NC}: terraform not installed"
fi

step "15. No hardcoded secrets in repository"
check "no_secrets" python3 - <<'PY'
import re, sys
from pathlib import Path
patterns = re.compile(r"(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|-----BEGIN (RSA |EC )?PRIVATE KEY-----)")
bad = []
for f in Path(".").rglob("*"):
    if not f.is_file() or ".git" in f.parts or "__pycache__" in f.parts or f.suffix == ".pyc":
        continue
    if "DO_NOT_GENERATE" in str(f) or "anti-patterns" in str(f):
        continue
    try:
        text = f.read_text(errors="ignore")
    except Exception:
        continue
    for i, line in enumerate(text.splitlines(), 1):
        if patterns.search(line):
            bad.append(f"{f}:{i}")
if bad:
    print("Potential secrets found:")
    for b in bad[:10]:
        print(f"  - {b}")
    sys.exit(1)
print("No secrets found")
PY

step "Summary"
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}ALL CHECKS PASSED${NC}"
  exit 0
else
  echo -e "${RED}$FAILED CHECK(S) FAILED${NC}"
  exit 1
fi
