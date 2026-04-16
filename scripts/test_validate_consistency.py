#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import render_readme_skills
import validate_consistency


def write_min_readme(path: Path, payload: dict) -> None:
    template = """# Test\n\n<!-- SKILLS_LIST_START -->\n\n<!-- SKILLS_LIST_END -->\n"""
    block_lines = render_readme_skills.build_skills_block(payload)
    content = render_readme_skills.replace_block(template, block_lines)
    path.write_text(content, encoding="utf-8")


def write_min_index(path: Path) -> dict:
    payload = {
        "categories": [
            {
                "name": "Tool",
                "items": [
                    {
                        "id": "demo-skill",
                        "url": "https://github.com/example/demo/tree/main/skills/demo-skill",
                        "desc": "demo",
                    }
                ],
            }
        ]
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


class ValidateIndexTests(unittest.TestCase):
    def test_reports_duplicate_ids_across_categories(self) -> None:
        payload = {
            "categories": [
                {
                    "name": "Tool",
                    "items": [{"id": "same", "url": "https://github.com/a/b"}],
                },
                {
                    "name": "Web",
                    "items": [{"id": "same", "url": "https://github.com/c/d"}],
                },
            ]
        }
        errors, _ = validate_consistency.validate_index(payload)
        self.assertTrue(any("跨分类重复" in e for e in errors))

    def test_reports_invalid_cli_shape(self) -> None:
        payload = {
            "categories": [
                {
                    "name": "Tool",
                    "items": [
                        {
                            "id": "demo",
                            "url": "https://github.com/a/b",
                            "cli": {"name": "bad-type"},
                        }
                    ],
                }
            ]
        }
        errors, _ = validate_consistency.validate_index(payload)
        self.assertTrue(any("cli 必须是数组" in e for e in errors))


class ValidateExternalSkillsTests(unittest.TestCase):
    def test_reports_missing_skill_dirs(self) -> None:
        expected = {"Tool": {"a", "b"}}
        actual = {"Tool": {"a"}}
        errors = validate_consistency.validate_external_skills(expected, actual)
        self.assertEqual(len(errors), 1)
        self.assertIn("b", errors[0])

    def test_scan_external_skills_supports_wrapped_skill_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wrapped = root / "external-skills" / "Design" / "ui-ux-pro-max" / "ui-ux-pro-max"
            wrapped.mkdir(parents=True)
            (wrapped / "SKILL.md").write_text("# wrapped", encoding="utf-8")

            actual = validate_consistency.scan_external_skills(root)
            self.assertIn("Design", actual)
            self.assertIn("ui-ux-pro-max", actual["Design"])


class BuildExpectedSkillIdsTests(unittest.TestCase):
    def test_uses_combo_pack_subskills_from_cache(self) -> None:
        payload = {
            "categories": [
                {
                    "name": "Web",
                    "items": [
                        {
                            "id": "next-skills",
                            "url": "https://github.com/vercel-labs/next-skills",
                        }
                    ],
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / ".cache" / "vercel-labs-next-skills" / "skills"
            for name in ("next-best-practices", "next-upgrade"):
                d = base / name
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(f"# {name}", encoding="utf-8")

            expected = validate_consistency.build_expected_skill_ids(payload, root)
            self.assertEqual(
                expected,
                {"Web": {"next-best-practices", "next-upgrade"}},
            )


class MainFlowTests(unittest.TestCase):
    def test_main_returns_0_when_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = write_min_index(root / "index.json")
            write_min_readme(root / "README.md", payload)

            skill_dir = root / "external-skills" / "Tool" / "demo-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# demo", encoding="utf-8")

            rc = validate_consistency.main(["--root", str(root)])
            self.assertEqual(rc, 0)

    def test_main_returns_1_when_readme_outdated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_min_index(root / "index.json")
            (root / "README.md").write_text("# stale\n", encoding="utf-8")

            skill_dir = root / "external-skills" / "Tool" / "demo-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# demo", encoding="utf-8")

            rc = validate_consistency.main(["--root", str(root)])
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
