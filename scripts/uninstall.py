#!/usr/bin/env python3
"""卸载技能脚本：通过 npx skills remove 移除已安装的技能。

用法：
  --skill <id>       卸载单个技能
  --category <name>  卸载指定分类下全部技能（从 index.json 解析）
  --dry-run          仅打印命令，不实际执行
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_index(root: Path) -> dict:
    index_path = root / "index.json"
    if not index_path.is_file():
        raise ValueError(f"未找到 index.json: {index_path}")
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("categories"), list):
        raise ValueError("index.json 格式错误: categories 必须是数组")
    return payload


def get_category_skill_ids(root: Path, category_name: str) -> list[str]:
    """从 index.json 中查找指定分类的所有 skill id。"""
    payload = load_index(root)
    for category in payload["categories"]:
        if str(category.get("name", "")).strip() == category_name:
            items = category.get("items", [])
            ids = [str(item.get("id", "")).strip() for item in items if item.get("id")]
            if not ids:
                raise ValueError(f"分类 {category_name} 下没有可卸载的技能")
            return ids
    raise ValueError(f"未找到分类: {category_name}")


def build_remove_command(skill_id: str, global_install: bool, agents: list[str]) -> list[str]:
    cmd: list[str] = ["npx", "skills", "remove", skill_id]
    if global_install:
        cmd.append("-g")
    for agent in agents:
        cmd.extend(["-a", agent])
    cmd.append("-y")
    return cmd


def ensure_npx_available() -> None:
    try:
        subprocess.run(
            ["npx", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError("未检测到可用的 npx，请先安装 Node.js/npm") from exc


def execute_removes(
    skill_ids: list[str],
    global_install: bool,
    agents: list[str],
    dry_run: bool,
) -> list[str]:
    """执行卸载，遇错继续并返回失败的 skill id 列表。"""
    failures: list[str] = []
    for skill_id in skill_ids:
        cmd = build_remove_command(skill_id, global_install, agents)
        print(f"[INFO] 卸载技能: {skill_id}")
        print(f"[CMD]  {' '.join(cmd)}")
        if dry_run:
            continue
        result = subprocess.run(cmd)
        if result.returncode != 0:
            failures.append(skill_id)
            print(f"[WARN] 卸载失败: {skill_id}", file=sys.stderr)
    return failures


def normalize_agents(raw_agents: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw in raw_agents:
        for item in raw.split(","):
            agent = item.strip()
            if agent:
                normalized.append(agent)
    return normalized


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从 Agent 中移除已安装的技能（封装 npx skills remove）"
    )
    parser.add_argument("--skill", help="卸载指定技能 id")
    parser.add_argument("--category", help="卸载指定分类下的全部技能")
    parser.add_argument("-g", "--global", dest="global_install", action="store_true")
    parser.add_argument("-a", "--agent", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true", help="仅打印命令，不实际执行")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if bool(args.skill) == bool(args.category):
        raise ValueError("必须且只能指定 --skill 或 --category 其中一个")

    agents = normalize_agents(list(args.agent))

    if args.skill:
        skill_ids = [args.skill.strip()]
    else:
        skill_ids = get_category_skill_ids(ROOT, str(args.category).strip())

    ensure_npx_available()

    if args.dry_run:
        print("[INFO] --dry-run 模式，仅打印命令，不实际执行")

    failures = execute_removes(skill_ids, args.global_install, agents, args.dry_run)

    if args.dry_run:
        print(f"[INFO] 共 {len(skill_ids)} 条卸载命令（dry-run）")
        return 0

    if failures:
        print(f"[ERROR] 以下技能卸载失败: {', '.join(failures)}", file=sys.stderr)
        return 1

    print("[INFO] 卸载完成")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (ValueError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
