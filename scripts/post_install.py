#!/usr/bin/env python3
"""安装后检查脚本：验证 todo.md 中所需的外部 CLI 工具是否已安装。

所有检查项来源于 scripts/todo.md，缺失时会打印对应的安装命令提示。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass


@dataclass
class CliCheck:
    """代表一个需要检查的 CLI 工具。"""

    name: str
    """命令名（用于 shutil.which 检测）。"""
    install_hint: str
    """未安装时展示的安装命令。"""
    description: str
    """用途描述。"""


REQUIRED_CLIS: list[CliCheck] = [
    CliCheck(
        name="ctx7",
        install_hint="npm install -g ctx7@latest",
        description="Context7 CLI（文档检索）",
    ),
    CliCheck(
        name="tvly",
        install_hint="curl -fsSL https://cli.tavily.com/install.sh | bash",
        description="Tavily 搜索 CLI",
    ),
    CliCheck(
        name="agent-browser",
        install_hint="npm install -g agent-browser && agent-browser install",
        description="浏览器自动化 CLI",
    ),
]


def check_cli(cli: CliCheck) -> bool:
    """返回 True 表示 CLI 已安装。"""
    return shutil.which(cli.name) is not None


def run_checks(clis: list[CliCheck]) -> list[CliCheck]:
    """返回未安装的 CLI 列表。"""
    return [cli for cli in clis if not check_cli(cli)]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="安装后检查：验证必要的外部 CLI 工具是否可用"
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    parse_args(argv)
    missing = run_checks(REQUIRED_CLIS)

    if not missing:
        print("[INFO] 所有必要 CLI 工具已就绪")
        return 0

    print(f"[WARN] 检测到 {len(missing)} 个未安装的 CLI 工具：", file=sys.stderr)
    for cli in missing:
        print(f"  - {cli.name}（{cli.description}）", file=sys.stderr)
        print(f"    安装命令：{cli.install_hint}", file=sys.stderr)

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
