import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import install


class ScanLocalSkillsTests(unittest.TestCase):
    def test_finds_skills_with_skill_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills_dir = root / "skills"
            s1 = skills_dir / "code-refactor"
            s1.mkdir(parents=True)
            (s1 / "SKILL.md").write_text("# code-refactor", encoding="utf-8")
            # dir without SKILL.md should be excluded
            s2 = skills_dir / "no-skill"
            s2.mkdir()
            result = install.scan_local_skills(root)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, "code-refactor")

    def test_returns_empty_when_no_skills_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = install.scan_local_skills(Path(tmp))
            self.assertEqual(result, [])

    def test_results_are_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills_dir = root / "skills"
            for name in ("zzz", "aaa", "mmm"):
                d = skills_dir / name
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(f"# {name}", encoding="utf-8")
            result = install.scan_local_skills(root)
            self.assertEqual([d.name for d in result], ["aaa", "mmm", "zzz"])


class ScanExternalSkillsTests(unittest.TestCase):
    def test_finds_category_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "external-skills" / "Tool" / "pnpm"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# pnpm", encoding="utf-8")
            result = install.scan_external_skills(root)
            self.assertIn("Tool", result)
            self.assertEqual(len(result["Tool"]), 1)
            self.assertEqual(result["Tool"][0].name, "pnpm")

    def test_excludes_category_with_no_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            empty_cat = root / "external-skills" / "Empty"
            (empty_cat / "not-a-skill").mkdir(parents=True)
            result = install.scan_external_skills(root)
            self.assertNotIn("Empty", result)

    def test_returns_empty_when_no_external_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = install.scan_external_skills(Path(tmp))
            self.assertEqual(result, {})

    def test_multiple_categories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for cat, skill in [("Tool", "pnpm"), ("Web", "nuxt")]:
                d = root / "external-skills" / cat / skill
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(f"# {skill}", encoding="utf-8")
            result = install.scan_external_skills(root)
            self.assertIn("Tool", result)
            self.assertIn("Web", result)


class CopySkillTests(unittest.TestCase):
    def test_copies_skill_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "my-skill"
            src.mkdir()
            (src / "SKILL.md").write_text("# test", encoding="utf-8")
            target = root / "target"
            target.mkdir()
            install.copy_skill(src, target)
            self.assertTrue((target / "my-skill" / "SKILL.md").exists())

    def test_overwrites_existing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "my-skill"
            src.mkdir()
            (src / "SKILL.md").write_text("# new content", encoding="utf-8")
            target = root / "target"
            existing = target / "my-skill"
            existing.mkdir(parents=True)
            (existing / "OLD.md").write_text("old", encoding="utf-8")
            install.copy_skill(src, target)
            self.assertTrue((target / "my-skill" / "SKILL.md").exists())
            self.assertFalse((target / "my-skill" / "OLD.md").exists())


class InstallSkillsTests(unittest.TestCase):
    def test_installs_all_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_a = root / "src" / "skill-a"
            src_b = root / "src" / "skill-b"
            for d in (src_a, src_b):
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(f"# {d.name}", encoding="utf-8")
            target = root / "target"
            target.mkdir()
            failures = install.install_skills([src_a, src_b], target)
            self.assertEqual(failures, [])
            self.assertTrue((target / "skill-a" / "SKILL.md").exists())
            self.assertTrue((target / "skill-b" / "SKILL.md").exists())

    def test_collects_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "bad-skill"
            src.mkdir()
            # target is a file, not a dir → copy_skill will raise
            target = root / "target.txt"
            target.write_text("not a dir", encoding="utf-8")
            failures = install.install_skills([src], target)
            self.assertEqual(failures, ["bad-skill"])


class CreateSymlinksTests(unittest.TestCase):
    def test_creates_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target_dir = root / "agents" / "skills"
            skill_dir = target_dir / "my-skill"
            skill_dir.mkdir(parents=True)
            link_dir = root / "claude" / "skills"
            install.create_symlinks(target_dir, [link_dir])
            link = link_dir / "my-skill"
            self.assertTrue(link.is_symlink())
            self.assertEqual(
                Path(os.readlink(str(link))).resolve(), skill_dir.resolve()
            )

    def test_overwrites_existing_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target_dir = root / "agents" / "skills"
            skill_dir = target_dir / "my-skill"
            skill_dir.mkdir(parents=True)
            link_dir = root / "claude" / "skills"
            link_dir.mkdir(parents=True)
            old_target = root / "old-target"
            old_target.mkdir()
            old_link = link_dir / "my-skill"
            os.symlink(str(old_target), str(old_link))
            install.create_symlinks(target_dir, [link_dir])
            self.assertTrue(old_link.is_symlink())
            self.assertEqual(
                Path(os.readlink(str(old_link))).resolve(), skill_dir.resolve()
            )

    def test_creates_symlink_in_multiple_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target_dir = root / "agents" / "skills"
            (target_dir / "my-skill").mkdir(parents=True)
            link_a = root / "claude" / "skills"
            link_b = root / "codex" / "skills"
            install.create_symlinks(target_dir, [link_a, link_b])
            self.assertTrue((link_a / "my-skill").is_symlink())
            self.assertTrue((link_b / "my-skill").is_symlink())

    def test_skips_when_target_not_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # target_dir does not exist
            target_dir = root / "nonexistent"
            link_dir = root / "claude" / "skills"
            # Should not raise
            install.create_symlinks(target_dir, [link_dir])
            self.assertFalse(link_dir.exists())


class MainTests(unittest.TestCase):

    def test_installs_local_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "skills" / "my-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# my-skill", encoding="utf-8")
            target = root / "target"
            target.mkdir()
            with patch.object(install, "ROOT", root):
                with patch.object(install, "SYMLINK_DIRS", []):
                    rc = install.main(["--target", str(target), "--no-interactive"])
            self.assertEqual(rc, 0)
            self.assertTrue((target / "my-skill" / "SKILL.md").exists())

    def test_returns_error_for_unknown_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target"
            target.mkdir()
            with patch.object(install, "ROOT", root):
                rc = install.main(["--target", str(target), "--category", "NoSuchCat"])
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
