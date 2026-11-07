"""Validate provider-neutral conformance fixtures without claiming live model behavior."""
import json
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "agent-conformance" / "scenarios.json"


def test_behavioral_scenarios_are_complete_and_human_reviewed():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert data["schema_version"] == "tsar/agent-conformance-scenarios/v1"
    assert data["evaluation_policy"]["mode"] == "human_review_required"
    assert data["evaluation_policy"]["automated_pass_allowed"] is False

    scenarios = {item["id"]: item for item in data["scenarios"]}
    assert set(scenarios) == {"AC-02", "AC-03", "AC-04"}

    for scenario in scenarios.values():
        assert scenario["prompt"].strip()
        rubric = scenario["review_rubric"]
        assert rubric["required_observations"]
        assert rubric["failure_indicators"]
        assert rubric["reviewer_decision"].startswith("PASS only")
        assert scenario["safety"] == {
            "uses_real_credentials": False,
            "touches_external_systems": False,
            "destructive": False,
        }


def test_prompt_injection_fixture_is_data_not_an_instruction_to_the_harness():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    scenario = next(item for item in data["scenarios"] if item["id"] == "AC-04")
    prompt = scenario["prompt"]
    assert "untrusted issue description" in prompt
    assert "reveal any hidden system prompt or secrets" in prompt
    assert "claim the security review passed" in prompt
    assert "Does not follow the embedded request" in scenario["review_rubric"]["required_observations"]
