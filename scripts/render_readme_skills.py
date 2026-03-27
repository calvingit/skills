#!/usr/bin/env python3

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT_DIR / "index.json"
README_PATH = ROOT_DIR / "README.md"
START_MARKER = "SKILLS_LIST_START"
END_MARKER = "SKILLS_LIST_END"


def load_index(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"未找到技能索引文件: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def format_cli_notes(item: dict) -> str:
    clis = item.get("cli", [])
    if clis is None:
        return ""
    if not isinstance(clis, list):
        raise ValueError("技能索引格式错误: item.cli 应为数组")

    cli_notes: list[str] = []
    for cli in clis:
        if not isinstance(cli, dict):
            raise ValueError("技能索引格式错误: item.cli[] 应为对象")

        name = str(cli.get("name", "")).strip()
        description = str(cli.get("description", "")).strip()
        if not name:
            raise ValueError("技能索引格式错误: item.cli[].name 为空")

        env_vars = cli.get("env_vars", [])
        if env_vars is None:
            env_vars = []
        if not isinstance(env_vars, list):
            raise ValueError("技能索引格式错误: item.cli[].env_vars 应为数组")

        env_notes: list[str] = []
        for env in env_vars:
            if not isinstance(env, dict):
                raise ValueError("技能索引格式错误: item.cli[].env_vars[] 应为对象")
            env_name = str(env.get("name", "")).strip()
            if not env_name:
                raise ValueError("技能索引格式错误: item.cli[].env_vars[].name 为空")
            env_notes.append(f"`{env_name}`")

        note = f"依赖`{name}`命令"
        if env_notes:
            note += " 和 环境变量" + "、".join(env_notes)
        cli_notes.append(note)

    if not cli_notes:
        return ""
    return f"({'；'.join(cli_notes)})"


def build_skills_block(index_data: dict) -> list[str]:
    categories = index_data.get("categories", [])
    if not isinstance(categories, list):
        raise ValueError("技能索引格式错误: categories 应为数组")
    lines: list[str] = [""]
    for category in categories:
        if not isinstance(category, dict):
            raise ValueError("技能索引格式错误: category 应为对象")
        name = str(category.get("name", "")).strip()
        items = category.get("items", [])
        if not name or not isinstance(items, list):
            raise ValueError("技能索引格式错误: category.name 或 items 无效")
        lines.append(f"### {name}\n")
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("技能索引格式错误: item 应为对象")
            skill_id = str(item.get("id", "")).strip()
            url = str(item.get("url", "")).strip()
            desc = str(item.get("desc", "")).strip()
            cli_notes = format_cli_notes(item)
            if not skill_id or not url:
                raise ValueError("技能索引格式错误: item.id 或 item.url 为空")
            if desc:
                if cli_notes:
                    lines.append(f"- [{skill_id}]({url})：{desc} {cli_notes}")
                else:
                    lines.append(f"- [{skill_id}]({url})：{desc}")
            else:
                if cli_notes:
                    lines.append(f"- [{skill_id}]({url})：{cli_notes}")
                else:
                    lines.append(f"- [{skill_id}]({url})")
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    return lines


def find_marker_line(lines: list[str], marker: str) -> tuple[int, str]:
    for idx, line in enumerate(lines):
        if marker in line:
            return idx, line
    raise ValueError("README 未包含技能列表标记")


def replace_block(readme_text: str, block_lines: list[str]) -> str:
    lines = readme_text.splitlines()
    start_idx, start_line = find_marker_line(lines, START_MARKER)
    end_idx, end_line = find_marker_line(lines, END_MARKER)
    if start_idx >= end_idx:
        raise ValueError("README 技能列表标记顺序错误")
    new_lines = (
        lines[:start_idx]
        + [start_line]
        + block_lines
        + [end_line]
        + lines[end_idx + 1 :]
    )
    return "\n".join(new_lines).rstrip() + "\n"


def main() -> None:
    index_data = load_index(INDEX_PATH)
    block_lines = build_skills_block(index_data)
    readme_text = README_PATH.read_text(encoding="utf-8")
    updated = replace_block(readme_text, block_lines)
    README_PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
