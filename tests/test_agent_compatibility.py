"""Repository consistency checks for the shared 15-agent compatibility architecture."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "agent-compatibility-matrix.md"
REGISTRY = ROOT / "integrations" / "agent-profiles.json"
CANONICAL = ROOT / "prompts" / "universal.md"

EXPECTED = {
    "Claude (chat)": "claude",
    "Claude Code": "claude-code",
    "GPT": "gpt",
    "DeepSeek-Coder": "deepseek-coder",
    "Qwen-Coder": "qwen-coder",
    "Gemini": "gemini",
    "Llama": "llama",
    "Cursor": "cursor",
    "GitHub Copilot": "github-copilot",
    "Manus": "manus",
    "Windsurf": "windsurf",
    "SuperNinja": "superninja",
    "Replit Agent": "replit-agent",
    "Devin": "devin",
    "Kimi": "kimi",
}


class AgentCompatibilityArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = MATRIX.read_text(encoding="utf-8")
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.profiles = cls.registry["profiles"]

    def test_exactly_fifteen_unique_profiles_exist(self) -> None:
        self.assertEqual(self.registry["schema_version"], "1.0.0")
        self.assertEqual(self.registry["policy_source"], "prompts/universal.md")
        self.assertEqual(len(self.profiles), 15)
        names = [profile["name"] for profile in self.profiles]
        keys = [profile["key"] for profile in self.profiles]
        self.assertEqual(set(names), set(EXPECTED))
        self.assertEqual(len(set(keys)), 15)
        self.assertEqual({p["name"]: p["key"] for p in self.profiles}, EXPECTED)

    def test_all_profiles_share_the_single_canonical_instruction_source(self) -> None:
        self.assertTrue(CANONICAL.is_file())
        canonical = CANONICAL.read_text(encoding="utf-8")
        self.assertIn("single authoritative TSAR instruction set", canonical)
        for profile in self.profiles:
            with self.subTest(agent=profile["name"]):
                self.assertEqual(profile["canonical_instructions"], "prompts/universal.md")
                self.assertIn(profile["delivery"], {
                    "system_instructions", "project_instructions",
                    "repository_instructions", "agent_instructions",
                })
                self.assertTrue(profile["target"].strip())

    def test_legacy_prompt_paths_are_small_pointers_not_policy_copies(self) -> None:
        for profile in self.profiles:
            path = ROOT / "prompts" / (profile["key"] + ".md")
            with self.subTest(agent=profile["name"]):
                self.assertTrue(path.is_file())
                self.assertLess(path.stat().st_size, 1024)
                content = path.read_text(encoding="utf-8")
                self.assertIn("Legacy Compatibility Pointer", content)
                self.assertIn("universal.md", content)
                self.assertIn("not an independent TSAR policy", content)

    def test_only_claude_code_declares_the_optional_native_hook_adapter(self) -> None:
        hooked = [p["name"] for p in self.profiles if p["native_adapter"]]
        self.assertEqual(hooked, ["Claude Code"])
        self.assertTrue((ROOT / "integrations" / "claude-code" / "settings.json").is_file())

    def test_matrix_matches_registry_without_claiming_live_provider_proof(self) -> None:
        rows = [line for line in self.matrix.splitlines() if line.startswith("| ") and "prompts/universal.md" in line]
        parsed = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
        self.assertEqual(len(parsed), 15)
        self.assertEqual({row[0]: row[2] for row in parsed}, EXPECTED)
        self.assertIn("does not call providers", self.matrix)
        self.assertIn("Live provider conformance", self.matrix)
        self.assertIn("or establish live runtime conformance", self.matrix)
        self.assertIn("Instruction Source", self.matrix)


if __name__ == "__main__":
    unittest.main()
