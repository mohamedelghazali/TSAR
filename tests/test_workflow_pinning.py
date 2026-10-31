"""Supply-chain guardrails for GitHub Actions workflows."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
COMPOSITE_ACTIONS = ROOT / ".github" / "actions"


def test_all_external_actions_are_pinned_to_full_commit_shas():
    pattern = re.compile(r"^\s*uses:\s*([^#\s]+)", re.MULTILINE)
    violations = []
    files = list(WORKFLOWS.glob("*.yml")) + list(COMPOSITE_ACTIONS.rglob("action.yml"))
    for workflow in sorted(files):
        text = workflow.read_text(encoding="utf-8")
        for reference in pattern.findall(text):
            if reference.startswith("./"):
                continue
            if not re.search(r"@[0-9a-f]{40}$", reference):
                violations.append(f"{workflow.relative_to(ROOT)}: {reference}")
    assert not violations, "\n".join(violations)


def test_workflows_declare_explicit_token_permissions():
    for workflow in WORKFLOWS.glob("*.yml"):
        text = workflow.read_text(encoding="utf-8")
        assert re.search(r"^permissions:\s*$", text, re.MULTILINE), workflow.name


def test_workflows_do_not_download_moving_latest_binaries():
    for workflow in WORKFLOWS.glob("*.yml"):
        text = workflow.read_text(encoding="utf-8")
        assert "releases/latest" not in text, workflow.name
        assert "downloads/latest" not in text, workflow.name


def test_checkout_credentials_are_disabled_exactly_once_per_checkout():
    for workflow in WORKFLOWS.glob("*.yml"):
        text = workflow.read_text(encoding="utf-8")
        checkouts = text.count("uses: actions/checkout@")
        disabled = text.count("persist-credentials: false")
        assert disabled == checkouts, workflow.name


def test_pr_enforcement_scans_secure_examples_not_policy_documents():
    workflow = (WORKFLOWS / "enforce-on-pr.yml").read_text(encoding="utf-8")
    assert "review.py examples/secure" in workflow
    assert "review.py ." not in workflow
