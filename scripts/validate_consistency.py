#!/usr/bin/env python3
"""校验 index.json、README 以及 external-skills 目录的一致性。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import download
import render_readme_skills

ROOT = SCRIPT_DIR.parent
INDEX_PATH = ROOT / "index.json"
README_PATH = ROOT / "README.md"
EXTERNAL_SKILLS_DIR = ROOT / "external-skills"


def load_index(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"未找到索引文件: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("index.json 顶层必须是对象")
    return payload


def validate_index(payload: dict) -> tuple[list[str], dict[str, set[str]]]:
    errors: list[str] = []
    expected_ids: dict[str, set[str]] = {}

    categories = payload.get("categories")
    if not isinstance(categories, list):
        return ["index.json 格式错误: categories 必须是数组"], expected_ids

    category_names: set[str] = set()
    global_skill_ids: dict[str, str] = {}

    for cat_idx, category in enumerate(categories):
        path_prefix = f"categories[{cat_idx}]"
        if not isinstance(category, dict):
            errors.append(f"{path_prefix} 必须是对象")
            continue

        category_name = str(category.get("name", "")).strip()
        if not category_name:
            errors.append(f"{path_prefix}.name 不能为空")
            continue
        if category_name in category_names:
            errors.append(f"分类名重复: {category_name}")
            continue
        category_names.add(category_name)

        items = category.get("items")
        if not isinstance(items, list):
            errors.append(f"{path_prefix}.items 必须是数组")
            continue

        cat_skill_ids: set[str] = set()
        for item_idx, item in enumerate(items):
            item_prefix = f"{path_prefix}.items[{item_idx}]"
            if not isinstance(item, dict):
                errors.append(f"{item_prefix} 必须是对象")
                continue

            skill_id = str(item.get("id", "")).strip()
            url = str(item.get("url", "")).strip()
            if not skill_id:
                errors.append(f"{item_prefix}.id 不能为空")
                continue
            if not url:
                errors.append(f"{item_prefix}.url 不能为空")
                continue
            try:
                download.parse_skill_url(url)
            except ValueError as exc:
                errors.append(f"{item_prefix}.url 无法解析: {exc}")
                continue

            if skill_id in cat_skill_ids:
                errors.append(f"{category_name} 分类内 skill id 重复: {skill_id}")
            else:
                cat_skill_ids.add(skill_id)

            if skill_id in global_skill_ids and global_skill_ids[skill_id] != category_name:
                errors.append(
                    f"skill id 跨分类重复: {skill_id}（{global_skill_ids[skill_id]} 与 {category_name}）"
                )
            else:
                global_skill_ids[skill_id] = category_name

            clis = item.get("cli")
            if clis is not None and not isinstance(clis, list):
                errors.append(f"{item_prefix}.cli 必须是数组")
                continue

            for cli_idx, cli in enumerate(clis or []):
                cli_prefix = f"{item_prefix}.cli[{cli_idx}]"
                if not isinstance(cli, dict):
                    errors.append(f"{cli_prefix} 必须是对象")
                    continue
                cli_name = str(cli.get("name", "")).strip()
                if not cli_name:
                    errors.append(f"{cli_prefix}.name 不能为空")

                env_vars = cli.get("env_vars")
                if env_vars is not None and not isinstance(env_vars, list):
                    errors.append(f"{cli_prefix}.env_vars 必须是数组")
                    continue
                for env_idx, env in enumerate(env_vars or []):
                    env_prefix = f"{cli_prefix}.env_vars[{env_idx}]"
                    if not isinstance(env, dict):
                        errors.append(f"{env_prefix} 必须是对象")
                        continue
                    env_name = str(env.get("name", "")).strip()
                    if not env_name:
                        errors.append(f"{env_prefix}.name 不能为空")

        expected_ids[category_name] = cat_skill_ids

    return errors, expected_ids


def build_expected_skill_ids(payload: dict, root: Path) -> dict[str, set[str]]:
    expected: dict[str, set[str]] = {}
    cache_dir = root / ".cache"

    for category in payload.get("categories", []):
        if not isinstance(category, dict):
            continue
        category_name = str(category.get("name", "")).strip()
        if not category_name:
            continue

        category_expected = expected.setdefault(category_name, set())
        for item in category.get("items", []):
            if not isinstance(item, dict):
                continue

            skill_id = str(item.get("id", "")).strip()
            url = str(item.get("url", "")).strip()
            if not skill_id or not url:
                continue

            try:
                owner, repo, _, subpath = download.parse_skill_url(url)
            except ValueError:
                # URL 错误由 validate_index 报告；这里跳过推导。
                continue

            if subpath:
                category_expected.add(skill_id)
                continue

            repo_dir = cache_dir / download.make_cache_dir_name(owner, repo)
            skills_dir = repo_dir / "skills"
            if skills_dir.is_dir():
                subskill_dirs = sorted(
                    [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()]
                )
                if subskill_dirs:
                    for subskill in subskill_dirs:
                        category_expected.add(subskill.name)
                    continue

            # 缓存缺失或无法识别时，回退到 item.id，至少保证最小约束可校验。
            category_expected.add(skill_id)

    return expected


def scan_external_skills(root: Path) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    external_dir = root / "external-skills"
    if not external_dir.is_dir():
        return result

    for category_dir in sorted(external_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        skill_ids: set[str] = set()
        for skill_dir in sorted(category_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            if (skill_dir / "SKILL.md").is_file():
                skill_ids.add(skill_dir.name)
                continue

            wrapped = skill_dir / skill_dir.name / "SKILL.md"
            if wrapped.is_file():
                skill_ids.add(skill_dir.name)
        if skill_ids:
            result[category_dir.name] = skill_ids
    return result


def validate_external_skills(
    expected_ids: dict[str, set[str]],
    actual_ids: dict[str, set[str]],
) -> list[str]:
    errors: list[str] = []

    for category, expected in expected_ids.items():
        actual = actual_ids.get(category, set())
        missing = sorted(expected - actual)
        if missing:
            errors.append(
                f"external-skills 缺失 {category} 分类技能: {', '.join(missing)}"
            )

    return errors


def validate_readme_sync(payload: dict, readme_path: Path) -> list[str]:
    errors: list[str] = []
    if not readme_path.is_file():
        return [f"未找到 README 文件: {readme_path}"]

    readme_text = readme_path.read_text(encoding="utf-8")
    try:
        block_lines = render_readme_skills.build_skills_block(payload)
        expected_readme = render_readme_skills.replace_block(readme_text, block_lines)
    except ValueError as exc:
        return [f"README 标记区块校验失败: {exc}"]

    if expected_readme != readme_text:
        errors.append(
            "README 技能列表与 index.json 不一致，请运行: python3 scripts/render_readme_skills.py"
        )

    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验 index.json、README、external-skills 的一致性"
    )
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="仓库根目录（默认当前脚本上级目录）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出校验结果",
    )
    return parser.parse_args(argv)


def format_json_output(errors: list[str]) -> str:
    payload = {
        "status": "fail" if errors else "pass",
        "errors": errors,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()

    index_path = root / INDEX_PATH.name
    readme_path = root / README_PATH.name

    errors: list[str] = []
    try:
        payload = load_index(index_path)
    except (ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
        payload = {}

    if payload:
        index_errors, _ = validate_index(payload)
        errors.extend(index_errors)

        expected_ids = build_expected_skill_ids(payload, root)
        actual_ids = scan_external_skills(root)
        errors.extend(validate_external_skills(expected_ids, actual_ids))
        errors.extend(validate_readme_sync(payload, readme_path))
    else:
        # payload 无法加载时，后续校验无法进行。
        expected_ids = {}

    if args.json:
        print(format_json_output(errors))
    else:
        if errors:
            print("[ERROR] 一致性校验失败:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
        else:
            print("[INFO] 一致性校验通过")

    _ = expected_ids
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
