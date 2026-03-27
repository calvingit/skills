#!/usr/bin/env python3
"""Skills 安装脚本：从 index.json 读取技能列表并通过 npx skills add 安装。

默认行为：先安装 https://github.com/calvingit/skills，再安装 index.json 全部条目。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "index.json"
DEFAULT_SKILL_URL = "https://github.com/calvingit/skills"


def load_items(root: Path) -> list[dict[str, str]]:
    """从 index.json 扁平化读取所有技能条目，按 url 去重。"""
    index_path = root / "index.json"
    if not index_path.is_file():
        raise ValueError(f"未找到 index.json: {index_path}")

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    categories = payload.get("categories", [])
    if not isinstance(categories, list):
        raise ValueError("index.json 格式错误: categories 必须是数组")

    seen_urls: set[str] = set()
    items: list[dict[str, str]] = []
    for category in categories:
        if not isinstance(category, dict):
            continue
        for item in category.get("items", []):
            if not isinstance(item, dict):
                continue
            url = str(item.get("url", "")).strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            items.append(
                {
                    "id": str(item.get("id", "")).strip(),
                    "url": url,
                    "desc": str(item.get("desc", "")).strip(),
                }
            )
    return items


def build_install_command(
    url: str, global_install: bool, agents: list[str]
) -> list[str]:
    cmd: list[str] = ["npx", "skills", "add", url]
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


def execute_installs(
    items: list[dict[str, str]],
    global_install: bool,
    agents: list[str],
) -> tuple[list[str], list[str]]:
    """执行安装，返回(失败项, 成功安装的 skill id 列表)。"""
    failures: list[str] = []
    installed_skill_ids: list[str] = []
    for item in items:
        url = item["url"]
        skill_id = str(item.get("id", "")).strip()
        label = skill_id or url
        cmd = build_install_command(url, global_install, agents)
        print(f"[INFO] 安装技能: {label}")
        print(f"[CMD]  {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            failures.append(label)
            print(f"[WARN] 安装失败: {label}", file=sys.stderr)
            continue

        if skill_id:
            installed_skill_ids.append(skill_id)

    return failures, installed_skill_ids


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
        description="安装本仓库 Skills 到 Agent（封装 npx skills add）",
    )
    parser.add_argument(
        "--skip-default",
        action="store_true",
        help=f"跳过默认技能包（{DEFAULT_SKILL_URL}）",
    )
    parser.add_argument("-g", "--global", dest="global_install", action="store_true")
    parser.add_argument("-a", "--agent", action="append", default=[])
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    agents = normalize_agents(list(args.agent))

    ensure_npx_available()

    install_list: list[dict[str, str]] = []
    if not args.skip_default:
        install_list.append(
            {"id": "calvingit/skills", "url": DEFAULT_SKILL_URL, "desc": "默认技能包"}
        )
    install_list.extend(load_items(ROOT))

    failures, installed_skill_ids = execute_installs(
        install_list,
        args.global_install,
        agents,
    )

    print()

    # 安装完成后自动执行环境检查
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import post_install  # noqa: PLC0415

        check_argv: list[str] = []
        if installed_skill_ids:
            check_argv = ["--installed-skills", ",".join(installed_skill_ids)]
        check_rc = post_install.main(check_argv)
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] post_install 检查出错: {exc}", file=sys.stderr)
        check_rc = 0

    if failures:
        print(f"[ERROR] 以下技能安装失败: {', '.join(failures)}", file=sys.stderr)
        return 1

    print("[INFO] 安装完成")
    return check_rc


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (ValueError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
