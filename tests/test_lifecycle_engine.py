"""Tests for deterministic TSAR lifecycle planning."""
import importlib.util
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / "tools" / "tsar-cli" / "lifecycle_engine.py"
SPEC = importlib.util.spec_from_file_location("tsar_lifecycle_engine", MODULE)
engine = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = engine
SPEC.loader.exec_module(engine)


def test_explicit_domains_are_deduplicated_and_validated():
    plan = engine.classify_task("Build an API", ["api", "api"], available_domains=["api"])
    assert plan.domains == ["api"]


def test_unknown_manifest_domain_is_rejected():
    with pytest.raises(ValueError, match="unknown manifest domain"):
        engine.classify_task("Build an API", ["unknown"], available_domains=["api"])


def test_high_impact_adds_strict_gates():
    plan = engine.classify_task("Deploy payment service to production")
    assert plan.impact == "high"
    assert plan.strict_required is True
    assert "threat_model" in plan.required_gates
    assert "independent_security_review" in plan.required_gates


def test_domain_heuristics_are_conservative_and_manifest_aware():
    plan = engine.classify_task("Implement OAuth login API", available_domains=["iam", "api"])
    assert set(plan.domains) == {"iam", "api"}


@pytest.mark.parametrize(
    "source,target,expected",
    [
        ("intake", "preflight", True),
        ("preflight", "design_review", True),
        ("implementation", "verification", True),
        ("verification", "implementation", True),
        ("verification", "complete", False),
        ("complete", "implementation", False),
        ("intake", "release_review", False),
    ],
)
def test_transition_graph(source, target, expected):
    allowed, _ = engine.validate_transition(source, target)
    assert allowed is expected


def test_completion_requires_gate_confirmation():
    with pytest.raises(ValueError, match="all required gates"):
        engine.transition("release_review", "complete")
    assert engine.transition("release_review", "complete", gates_passed=True) == engine.LifecycleState.COMPLETE
