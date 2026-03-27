#!/usr/bin/env python3
"""安装后检查脚本：按已安装 Skill 动态验证所需外部 CLI 是否可用。"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CliCheck:
    """代表一个需要检查的 CLI 工具。"""

    name: str
    """命令名（用于 shutil.which 检测）。"""
    install_hint: str
    """未安装时展示的安装命令。"""
    description: str
    """用途描述。"""
    env_vars: list["EnvVarCheck"] = field(default_factory=list)
    """该 CLI 依赖的环境变量。"""


@dataclass
class EnvVarCheck:
    """代表一个需要检查的环境变量。"""

    name: str
    """环境变量名。"""
    export_hint: str
    """未设置时展示的 export 命令。"""
    description: str
    """用途描述。"""


ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "index.json"


def check_cli(cli: CliCheck) -> bool:
    """返回 True 表示 CLI 已安装。"""
    return shutil.which(cli.name) is not None


def run_checks(clis: list[CliCheck]) -> list[CliCheck]:
    """返回未安装的 CLI 列表。"""
    return [cli for cli in clis if not check_cli(cli)]


def find_missing_env_vars(clis: list[CliCheck]) -> dict[str, list[EnvVarCheck]]:
    """返回每个 CLI 缺失的环境变量。"""
    missing: dict[str, list[EnvVarCheck]] = {}
    for cli in clis:
        missing_vars: list[EnvVarCheck] = []
        for env in cli.env_vars:
            value = os.environ.get(env.name, "").strip()
            if not value:
                missing_vars.append(env)
        if missing_vars:
            missing[cli.name] = missing_vars
    return missing


def normalize_skill_ids(raw_values: list[str]) -> set[str]:
    """将逗号分隔或重复传入的 skill id 归一化为集合。"""
    normalized: set[str] = set()
    for raw in raw_values:
        for item in raw.split(","):
            skill_id = item.strip()
            if skill_id:
                normalized.add(skill_id)
    return normalized


def load_required_clis(installed_skill_ids: set[str] | None = None) -> list[CliCheck]:
    """从 index.json 读取 CLI 依赖并按 skill 过滤，按 name 去重。"""
    if not INDEX_PATH.is_file():
        raise ValueError(f"未找到 index.json: {INDEX_PATH}")

    payload = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    categories = payload.get("categories", [])
    if not isinstance(categories, list):
        raise ValueError("index.json 格式错误: categories 必须是数组")

    seen_cli_names: set[str] = set()
    required: list[CliCheck] = []
    for category in categories:
        if not isinstance(category, dict):
            continue
        items = category.get("items", [])
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            skill_id = str(item.get("id", "")).strip()
            if installed_skill_ids is not None and skill_id not in installed_skill_ids:
                continue

            clis = item.get("cli", [])
            if clis is None:
                continue
            if not isinstance(clis, list):
                raise ValueError("index.json 格式错误: item.cli 必须是数组")

            for cli in clis:
                if not isinstance(cli, dict):
                    raise ValueError("index.json 格式错误: item.cli[] 必须是对象")

                name = str(cli.get("name", "")).strip()
                if not name or name in seen_cli_names:
                    continue

                install_hint = str(cli.get("install_hint", "")).strip()
                description = str(cli.get("description", "")).strip()
                if not install_hint or not description:
                    raise ValueError(
                        "index.json 格式错误: item.cli[] 需包含 name/install_hint/description"
                    )

                env_vars_payload = cli.get("env_vars", [])
                if env_vars_payload is None:
                    env_vars_payload = []
                if not isinstance(env_vars_payload, list):
                    raise ValueError(
                        "index.json 格式错误: item.cli[].env_vars 必须是数组"
                    )

                env_vars: list[EnvVarCheck] = []
                for env_item in env_vars_payload:
                    if not isinstance(env_item, dict):
                        raise ValueError(
                            "index.json 格式错误: item.cli[].env_vars[] 必须是对象"
                        )

                    env_name = str(env_item.get("name", "")).strip()
                    export_hint = str(env_item.get("export_hint", "")).strip()
                    env_description = str(env_item.get("description", "")).strip()
                    if not env_name or not export_hint or not env_description:
                        raise ValueError(
                            "index.json 格式错误: item.cli[].env_vars[] 需包含 name/export_hint/description"
                        )

                    env_vars.append(
                        EnvVarCheck(
                            name=env_name,
                            export_hint=export_hint,
                            description=env_description,
                        )
                    )

                seen_cli_names.add(name)
                required.append(
                    CliCheck(
                        name=name,
                        install_hint=install_hint,
                        description=description,
                        env_vars=env_vars,
                    )
                )

    return required


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="安装后检查：验证必要的外部 CLI 工具是否可用"
    )
    parser.add_argument(
        "--installed-skills",
        action="append",
        default=[],
        help="仅检查这些 skill id 对应的 CLI 依赖（支持逗号分隔）",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    installed_skill_ids = normalize_skill_ids(list(args.installed_skills))
    filter_ids = installed_skill_ids if installed_skill_ids else None
    required_clis = load_required_clis(filter_ids)

    if not required_clis:
        print("[INFO] 本次安装未涉及需要额外 CLI 的 Skill")
        return 0

    missing = run_checks(required_clis)
    missing_env_vars = find_missing_env_vars(required_clis)

    if not missing and not missing_env_vars:
        print("[INFO] 所有必要 CLI 工具与环境变量已就绪")
        return 0

    if missing:
        print(f"[WARN] 检测到 {len(missing)} 个未安装的 CLI 工具：", file=sys.stderr)
        for cli in missing:
            print(f"  - {cli.name}（{cli.description}）", file=sys.stderr)
            print(f"    安装命令：{cli.install_hint}", file=sys.stderr)

    if missing_env_vars:
        print(
            f"[WARN] 检测到 {sum(len(v) for v in missing_env_vars.values())} 个未设置的环境变量：",
            file=sys.stderr,
        )
        for cli_name, env_vars in missing_env_vars.items():
            print(f"  - CLI: {cli_name}", file=sys.stderr)
            for env in env_vars:
                print(
                    f"    {env.name}（{env.description}）\n"
                    f"    设置命令：{env.export_hint}",
                    file=sys.stderr,
                )

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
