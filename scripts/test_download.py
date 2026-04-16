#!/usr/bin/env python3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import download


class ParseSkillUrlTests(unittest.TestCase):
    def test_url_with_subpath(self) -> None:
        owner, repo, branch, subpath = download.parse_skill_url(
            "https://github.com/antfu/skills/tree/main/skills/pnpm"
        )
        self.assertEqual(owner, "antfu")
        self.assertEqual(repo, "skills")
        self.assertEqual(branch, "main")
        self.assertEqual(subpath, "skills/pnpm")

    def test_url_without_subpath(self) -> None:
        owner, repo, branch, subpath = download.parse_skill_url(
            "https://github.com/op7418/humanizer-zh"
        )
        self.assertEqual(owner, "op7418")
        self.assertEqual(repo, "humanizer-zh")
        self.assertIsNone(branch)
        self.assertIsNone(subpath)

    def test_url_with_deep_subpath(self) -> None:
        owner, repo, branch, subpath = download.parse_skill_url(
            "https://github.com/wshobson/agents/tree/main/plugins/documentation-generation/skills/changelog-automation"
        )
        self.assertEqual(owner, "wshobson")
        self.assertEqual(repo, "agents")
        self.assertEqual(branch, "main")
        self.assertEqual(
            subpath,
            "plugins/documentation-generation/skills/changelog-automation",
        )

    def test_url_trailing_slash(self) -> None:
        owner, repo, branch, subpath = download.parse_skill_url(
            "https://github.com/tavily-ai/skills/"
        )
        self.assertEqual(owner, "tavily-ai")
        self.assertEqual(repo, "skills")
        self.assertIsNone(branch)
        self.assertIsNone(subpath)

    def test_invalid_url_raises(self) -> None:
        with self.assertRaises(ValueError):
            download.parse_skill_url("not-a-github-url")

    def test_invalid_non_github_url_raises(self) -> None:
        with self.assertRaises(ValueError):
            download.parse_skill_url("https://gitlab.com/foo/bar")


class MakeCacheDirNameTests(unittest.TestCase):
    def test_basic(self) -> None:
        self.assertEqual(download.make_cache_dir_name("antfu", "skills"), "antfu-skills")

    def test_with_special_chars(self) -> None:
        self.assertEqual(
            download.make_cache_dir_name("ChromeDevTools", "chrome-devtools-mcp"),
            "ChromeDevTools-chrome-devtools-mcp",
        )


class EnsureCategoryDirsTests(unittest.TestCase):
    def test_creates_category_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "external-skills").mkdir()
            payload = {
                "categories": [
                    {"name": "Tool", "items": []},
                    {"name": "Web", "items": []},
                ]
            }
            download.ensure_category_dirs(root, payload)
            self.assertTrue((root / "external-skills" / "Tool").is_dir())
            self.assertTrue((root / "external-skills" / "Web").is_dir())

    def test_existing_dir_not_raised(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "external-skills" / "Tool").mkdir(parents=True)
            payload = {"categories": [{"name": "Tool", "items": []}]}
            # Should not raise
            download.ensure_category_dirs(root, payload)

    def test_filter_by_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "external-skills").mkdir()
            payload = {
                "categories": [
                    {"name": "Tool", "items": []},
                    {"name": "Web", "items": []},
                ]
            }
            download.ensure_category_dirs(root, payload, category_filter="Tool")
            self.assertTrue((root / "external-skills" / "Tool").is_dir())
            self.assertFalse((root / "external-skills" / "Web").exists())


class CollectCloneTargetsTests(unittest.TestCase):
    def test_deduplicates_same_repo(self) -> None:
        payload = {
            "categories": [
                {
                    "name": "Tool",
                    "items": [
                        {
                            "id": "vitest",
                            "url": "https://github.com/antfu/skills/tree/main/skills/vitest",
                        },
                        {
                            "id": "pnpm",
                            "url": "https://github.com/antfu/skills/tree/main/skills/pnpm",
                        },
                    ],
                }
            ]
        }
        targets = download.collect_clone_targets(payload)
        self.assertEqual(len(targets), 1)
        self.assertIn("antfu-skills", targets)

    def test_multiple_repos(self) -> None:
        payload = {
            "categories": [
                {
                    "name": "Tool",
                    "items": [
                        {
                            "id": "vitest",
                            "url": "https://github.com/antfu/skills/tree/main/skills/vitest",
                        },
                        {
                            "id": "humanizer-zh",
                            "url": "https://github.com/op7418/humanizer-zh",
                        },
                    ],
                }
            ]
        }
        targets = download.collect_clone_targets(payload)
        self.assertEqual(len(targets), 2)
        self.assertIn("antfu-skills", targets)
        self.assertIn("op7418-humanizer-zh", targets)

    def test_category_filter(self) -> None:
        payload = {
            "categories": [
                {
                    "name": "Tool",
                    "items": [
                        {"id": "a", "url": "https://github.com/foo/bar"},
                    ],
                },
                {
                    "name": "Web",
                    "items": [
                        {"id": "b", "url": "https://github.com/baz/qux"},
                    ],
                },
            ]
        }
        targets = download.collect_clone_targets(payload, category_filter="Tool")
        self.assertIn("foo-bar", targets)
        self.assertNotIn("baz-qux", targets)

    def test_skips_invalid_urls(self) -> None:
        payload = {
            "categories": [
                {
                    "name": "Tool",
                    "items": [
                        {"id": "bad", "url": "not-a-url"},
                        {"id": "good", "url": "https://github.com/foo/bar"},
                    ],
                }
            ]
        }
        targets = download.collect_clone_targets(payload)
        self.assertEqual(len(targets), 1)
        self.assertIn("foo-bar", targets)


class IsSingleSkillTests(unittest.TestCase):
    def test_with_skill_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "SKILL.md").write_text("# skill", encoding="utf-8")
            self.assertTrue(download._is_single_skill(d))

    def test_with_references_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "references").mkdir()
            self.assertTrue(download._is_single_skill(d))

    def test_scripts_dir_alone_not_single(self) -> None:
        """scripts/ 独自存在不足以判断为单 skill（不应该干扰组合包判断）。"""
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "scripts").mkdir()
            # 没有 SKILL.md 和 references/ → 不是单 skill
            self.assertFalse(download._is_single_skill(d))

    def test_combo_pack_with_scripts_not_single(self) -> None:
        """chrome-devtools 场景：有 scripts/ 且有 skills/ ，应判为组合包而非单 skill。"""
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "scripts").mkdir()
            (d / "skills").mkdir()  # 调用方会先判断这个
            (d / "README.md").write_text("# combo", encoding="utf-8")
            self.assertFalse(download._is_single_skill(d))

    def test_combo_pack_not_single(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "skills").mkdir()
            (d / "README.md").write_text("# combo", encoding="utf-8")
            self.assertFalse(download._is_single_skill(d))


class CopySingleSkillTests(unittest.TestCase):
    def test_copies_only_relevant_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "my-repo"
            repo.mkdir()
            (repo / "SKILL.md").write_text("# skill", encoding="utf-8")
            (repo / "references").mkdir()
            (repo / "references" / "tips.md").write_text("tips", encoding="utf-8")
            (repo / "scripts").mkdir()
            (repo / "scripts" / "run.sh").write_text("#!/bin/sh", encoding="utf-8")
            (repo / "README.md").write_text("readme", encoding="utf-8")
            (repo / "LICENSE").write_text("MIT", encoding="utf-8")
            (repo / ".gitignore").write_text("node_modules/", encoding="utf-8")
            dst = root / "target" / "my-skill"
            download._copy_single_skill(repo, dst)
            self.assertTrue((dst / "SKILL.md").exists())
            self.assertTrue((dst / "references" / "tips.md").exists())
            self.assertTrue((dst / "scripts" / "run.sh").exists())
            self.assertFalse((dst / "README.md").exists())
            self.assertFalse((dst / "LICENSE").exists())
            self.assertFalse((dst / ".gitignore").exists())

    def test_overwrites_existing_dst(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "my-repo"
            repo.mkdir()
            (repo / "SKILL.md").write_text("# new", encoding="utf-8")
            dst = root / "target"
            dst.mkdir()
            (dst / "OLD.md").write_text("old", encoding="utf-8")
            download._copy_single_skill(repo, dst)
            self.assertTrue((dst / "SKILL.md").exists())
            self.assertFalse((dst / "OLD.md").exists())

    def test_handles_missing_optional_dirs(self) -> None:
        """references/ 和 scripts/ 不存在时不报错。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "my-repo"
            repo.mkdir()
            (repo / "SKILL.md").write_text("# minimal", encoding="utf-8")
            dst = root / "target"
            download._copy_single_skill(repo, dst)
            self.assertTrue((dst / "SKILL.md").exists())
            self.assertFalse((dst / "references").exists())
            self.assertFalse((dst / "scripts").exists())


class ExtractSkillsTests(unittest.TestCase):
    def _make_skill_src(self, parent: Path, name: str) -> Path:
        d = parent / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(f"# {name}", encoding="utf-8")
        return d

    def test_extracts_skill_with_subpath(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_dir = root / ".cache"
            ext_dir = root / "external-skills" / "Tool"
            ext_dir.mkdir(parents=True)
            self._make_skill_src(cache_dir / "antfu-skills" / "skills", "pnpm")
            payload = {
                "categories": [
                    {
                        "name": "Tool",
                        "items": [
                            {
                                "id": "pnpm",
                                "url": "https://github.com/antfu/skills/tree/main/skills/pnpm",
                            }
                        ],
                    }
                ]
            }
            failures = download.extract_skills(
                payload, cache_dir, root / "external-skills"
            )
            self.assertEqual(failures, [])
            self.assertTrue((ext_dir / "pnpm" / "SKILL.md").exists())

    def test_extracts_single_skill_no_subpath(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_dir = root / ".cache"
            ext_dir = root / "external-skills" / "Documentation"
            ext_dir.mkdir(parents=True)
            repo_dir = cache_dir / "op7418-humanizer-zh"
            repo_dir.mkdir(parents=True)
            (repo_dir / "SKILL.md").write_text("# humanizer", encoding="utf-8")
            # 无关文件不应被复制
            (repo_dir / "README.md").write_text("readme", encoding="utf-8")
            (repo_dir / "LICENSE").write_text("MIT", encoding="utf-8")
            payload = {
                "categories": [
                    {
                        "name": "Documentation",
                        "items": [
                            {
                                "id": "humanizer-zh",
                                "url": "https://github.com/op7418/humanizer-zh",
                            }
                        ],
                    }
                ]
            }
            failures = download.extract_skills(
                payload, cache_dir, root / "external-skills"
            )
            self.assertEqual(failures, [])
            self.assertTrue((ext_dir / "humanizer-zh" / "SKILL.md").exists())
            self.assertFalse((ext_dir / "humanizer-zh" / "README.md").exists())
            self.assertFalse((ext_dir / "humanizer-zh" / "LICENSE").exists())

    def test_combo_pack_with_scripts_not_treated_as_single(self) -> None:
        """chrome-devtools 场景：有 scripts/ 且有 skills/，应作组合包处理。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_dir = root / ".cache"
            ext_dir = root / "external-skills" / "Tool"
            ext_dir.mkdir(parents=True)
            repo_dir = cache_dir / "ChromeDevTools-chrome-devtools-mcp"
            (repo_dir / "scripts").mkdir(parents=True)
            (repo_dir / "scripts" / "build.sh").write_text("#!/bin/sh", encoding="utf-8")
            # 6 个 skill
            for name in ("a11y-debugging", "chrome-devtools", "memory-leak-debugging",
                         "chrome-devtools-cli", "debug-optimize-lcp", "troubleshooting"):
                d = repo_dir / "skills" / name
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(f"# {name}", encoding="utf-8")
            payload = {
                "categories": [
                    {
                        "name": "Tool",
                        "items": [
                            {
                                "id": "chrome-devtools",
                                "url": "https://github.com/ChromeDevTools/chrome-devtools-mcp",
                            }
                        ],
                    }
                ]
            }
            failures = download.extract_skills(
                payload, cache_dir, root / "external-skills"
            )
            self.assertEqual(failures, [])
            for name in ("a11y-debugging", "chrome-devtools", "memory-leak-debugging",
                         "chrome-devtools-cli", "debug-optimize-lcp", "troubleshooting"):
                self.assertTrue(
                    (ext_dir / name / "SKILL.md").exists(),
                    f"缺少 skill: {name}",
                )

    def test_extracts_combo_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_dir = root / ".cache"
            ext_dir = root / "external-skills" / "Tool"
            ext_dir.mkdir(parents=True)
            self._make_skill_src(cache_dir / "tavily-ai-skills" / "skills", "tavily-search")
            self._make_skill_src(cache_dir / "tavily-ai-skills" / "skills", "tavily-extract")
            payload = {
                "categories": [
                    {
                        "name": "Tool",
                        "items": [
                            {
                                "id": "tavily-search",
                                "url": "https://github.com/tavily-ai/skills",
                            }
                        ],
                    }
                ]
            }
            failures = download.extract_skills(
                payload, cache_dir, root / "external-skills"
            )
            self.assertEqual(failures, [])
            self.assertTrue((ext_dir / "tavily-search").is_dir())
            self.assertTrue((ext_dir / "tavily-extract").is_dir())

    def test_skips_clone_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_dir = root / ".cache"
            ext_dir = root / "external-skills" / "Tool"
            ext_dir.mkdir(parents=True)
            payload = {
                "categories": [
                    {
                        "name": "Tool",
                        "items": [
                            {
                                "id": "foo",
                                "url": "https://github.com/foo/bar",
                            }
                        ],
                    }
                ]
            }
            # foo-bar 被标记为克隆失败
            failures = download.extract_skills(
                payload,
                cache_dir,
                root / "external-skills",
                clone_failures={"foo-bar"},
            )
            # 已跳过，不计入 failures
            self.assertEqual(failures, [])

    def test_override_existing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_dir = root / ".cache"
            ext_dir = root / "external-skills" / "Tool"
            # 已存在旧版本
            old_skill = ext_dir / "pnpm"
            old_skill.mkdir(parents=True)
            (old_skill / "OLD.md").write_text("old", encoding="utf-8")

            self._make_skill_src(cache_dir / "antfu-skills" / "skills", "pnpm")
            payload = {
                "categories": [
                    {
                        "name": "Tool",
                        "items": [
                            {
                                "id": "pnpm",
                                "url": "https://github.com/antfu/skills/tree/main/skills/pnpm",
                            }
                        ],
                    }
                ]
            }
            download.extract_skills(payload, cache_dir, root / "external-skills")
            self.assertTrue((ext_dir / "pnpm" / "SKILL.md").exists())
            self.assertFalse((ext_dir / "pnpm" / "OLD.md").exists())


class CloneReposTests(unittest.TestCase):
    def test_skips_existing_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp) / ".cache"
            existing = cache_dir / "antfu-skills"
            existing.mkdir(parents=True)
            targets = {
                "antfu-skills": {
                    "owner": "antfu",
                    "repo": "skills",
                    "branch": "main",
                    "url": "https://github.com/antfu/skills.git",
                }
            }
            with patch("download.subprocess.run") as mock_run:
                failures = download.clone_repos(cache_dir, targets)
            mock_run.assert_not_called()
            self.assertEqual(failures, [])

    def test_returns_failure_on_nonzero_returncode(self) -> None:
        import types

        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp) / ".cache"
            targets = {
                "foo-bar": {
                    "owner": "foo",
                    "repo": "bar",
                    "branch": None,
                    "url": "https://github.com/foo/bar.git",
                }
            }
            with patch(
                "download.subprocess.run",
                return_value=types.SimpleNamespace(returncode=1),
            ):
                failures = download.clone_repos(cache_dir, targets)
            self.assertEqual(failures, ["foo-bar"])


class PruneExternalSkillsTests(unittest.TestCase):
    def test_collect_expected_and_prune_removes_stale_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_dir = root / ".cache"
            ext_cat = root / "external-skills" / "Tool"
            ext_cat.mkdir(parents=True)

            # 组合包缓存：skills/ 下包含两个 skill
            for name in ("tavily-search", "tavily-extract"):
                d = cache_dir / "tavily-ai-skills" / "skills" / name
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(f"# {name}", encoding="utf-8")

            # 现有目录里包含一个过期 skill
            (ext_cat / "tavily-search").mkdir()
            (ext_cat / "tavily-extract").mkdir()
            (ext_cat / "legacy-skill").mkdir()

            payload = {
                "categories": [
                    {
                        "name": "Tool",
                        "items": [
                            {
                                "id": "tavily-search",
                                "url": "https://github.com/tavily-ai/skills",
                            }
                        ],
                    }
                ]
            }

            expected_map, unsafe_categories = download.collect_expected_skill_dirs(
                payload,
                cache_dir,
            )
            self.assertEqual(unsafe_categories, set())
            self.assertEqual(
                expected_map["Tool"],
                {"tavily-search", "tavily-extract"},
            )

            download.prune_external_skills(
                root / "external-skills",
                expected_map,
                unsafe_categories,
            )

            self.assertTrue((ext_cat / "tavily-search").exists())
            self.assertTrue((ext_cat / "tavily-extract").exists())
            self.assertFalse((ext_cat / "legacy-skill").exists())

    def test_skip_prune_when_category_is_unsafe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_dir = root / ".cache"
            ext_cat = root / "external-skills" / "Tool"
            ext_cat.mkdir(parents=True)

            # 缓存缺失：无法可靠推导组合包真实 skill 集
            payload = {
                "categories": [
                    {
                        "name": "Tool",
                        "items": [
                            {
                                "id": "tavily-search",
                                "url": "https://github.com/tavily-ai/skills",
                            }
                        ],
                    }
                ]
            }

            # 现有目录应保持不变
            (ext_cat / "legacy-skill").mkdir()

            expected_map, unsafe_categories = download.collect_expected_skill_dirs(
                payload,
                cache_dir,
            )
            self.assertIn("Tool", unsafe_categories)

            download.prune_external_skills(
                root / "external-skills",
                expected_map,
                unsafe_categories,
            )

            self.assertTrue((ext_cat / "legacy-skill").exists())


if __name__ == "__main__":
    unittest.main()
