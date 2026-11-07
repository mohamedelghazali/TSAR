"""Repository-level consistency checks for the 15 documented agent prompt integrations.

These tests deliberately do not claim that external providers were launched or obeyed TSAR.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "agent-compatibility-matrix.md"

EXPECTED_PROMPTS = {
    "Claude (chat)": "prompts/claude.md",
    "Claude Code": "prompts/claude-code.md",
    "GPT": "prompts/gpt.md",
    "DeepSeek-Coder": "prompts/deepseek-coder.md",
    "Qwen-Coder": "prompts/qwen-coder.md",
    "Gemini": "prompts/gemini.md",
    "Llama": "prompts/llama.md",
    "Cursor": "prompts/cursor.md",
    "GitHub Copilot": "prompts/github-copilot.md",
    "Manus": "prompts/manus.md",
    "Windsurf": "prompts/windsurf.md",
    "SuperNinja": "prompts/superninja.md",
    "Replit Agent": "prompts/replit-agent.md",
    "Devin": "prompts/devin.md",
    "Kimi": "prompts/kimi.md",
}


class AgentCompatibilityInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = MATRIX.read_text(encoding="utf-8")

    def test_exactly_fifteen_unique_agents_are_documented(self) -> None:
        rows = re.findall(r"^\| ([^|]+) \| (prompts/[^|]+) \|", self.matrix, re.MULTILINE)
        self.assertEqual(len(rows), 15, "compatibility matrix must contain exactly 15 agent rows")
        names = [name.strip() for name, _ in rows]
        self.assertEqual(len(set(names)), 15, "agent names in the matrix must be unique")
        self.assertEqual(dict((name.strip(), path.strip()) for name, path in rows), EXPECTED_PROMPTS)

    def test_every_matrix_prompt_exists_and_is_nonempty(self) -> None:
        for agent, relative_path in EXPECTED_PROMPTS.items():
            with self.subTest(agent=agent):
                prompt = ROOT / relative_path
                self.assertTrue(prompt.is_file(), f"missing prompt for {agent}: {relative_path}")
                self.assertGreater(prompt.stat().st_size, 0, f"empty prompt for {agent}: {relative_path}")

    def test_only_claude_code_is_documented_as_having_the_native_hook_profile(self) -> None:
        rows = re.findall(r"^\| ([^|]+) \| (prompts/[^|]+) \|[^\n]*$", self.matrix, re.MULTILINE)
        hook_agents = [
            name.strip()
            for name, _ in rows
            if "optional native TSAR hooks" in next(
                line for line in self.matrix.splitlines()
                if line.startswith(f"| {name.strip()} |")
            )
        ]
        self.assertEqual(hook_agents, ["Claude Code"])
        self.assertIn("not a shared hook implementation for the other 14 entries", self.matrix)

    def test_matrix_explicitly_separates_inventory_from_live_provider_proof(self) -> None:
        required_statements = (
            "repository consistency only",
            "does not call any provider",
            "Live provider conformance",
            "authenticated, supported environment",
            "not live authenticated-provider proof",
        )
        for statement in required_statements:
            with self.subTest(statement=statement):
                self.assertIn(statement, self.matrix)


if __name__ == "__main__":
    unittest.main()


"""Repository-level checks for the agent runtime conformance plan."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "agent-runtime-conformance-plan.md"


def test_runtime_conformance_plan_covers_all_fifteen_inventory_entries():
    text = PLAN.read_text(encoding="utf-8")
    names = (
        "Claude (chat)", "Claude Code", "GPT", "DeepSeek-Coder", "Qwen-Coder",
        "Gemini", "Llama", "Cursor", "GitHub Copilot", "Manus", "Windsurf",
        "SuperNinja", "Replit Agent", "Devin", "Kimi",
    )
    for name in names:
        assert f"| {name} |" in text


def test_runtime_conformance_plan_separates_live_tests_from_ci():
    text = PLAN.read_text(encoding="utf-8")
    for required in (
        "Standard conformance scenarios",
        "Evidence record",
        "CI versus live provider testing",
        "NOT_RUN",
        "NOT_APPLICABLE",
        "authenticated",
        "immutable commit SHA",
        "three times",
        "Do not make all 15 live tests mandatory",
    ):
        assert required in text


def test_plan_does_not_claim_all_providers_have_runtime_enforcement():
    text = PLAN.read_text(encoding="utf-8")
    assert "No other provider should be marked live-tested" in text
    assert "A chat-only interface with no supported interception mechanism may remain E0/E1" in text
