#!/usr/bin/env python3
"""Skill 安装脚本：从本地 skills/ 和 external-skills/ 目录复制 skill 到目标目录，
并为多个 agent 目录创建软链接。

默认目标目录：~/.agents/skills
软链接目录：~/.claude/skills、~/.codex/skills、~/.hermes/skills

用法：
  python3 scripts/install.py                       # 交互式选择外部 skill 分类
  python3 scripts/install.py --no-interactive      # 安装全部（含所有外部 skill）
  python3 scripts/install.py --category Web        # 安装指定外部 skill 分类
  python3 scripts/install.py --target /custom/dir  # 指定安装目标目录
"""

from __future__ import annotations

import argparse
import curses
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL_SKILLS_DIR = ROOT / "skills"
EXTERNAL_SKILLS_DIR = ROOT / "external-skills"

DEFAULT_TARGET = Path.home() / ".agents" / "skills"
# Agent 目标目录及模式配置
_AGENT_DIR: dict[str, Path] = {
    "claude": Path.home() / ".claude" / "skills",
    "codex": Path.home() / ".codex" / "skills",
    "hermes": Path.home() / ".hermes" / "skills",
}
_AGENT_DESC: dict[str, str] = {
    "claude": "平铺模式（每个 skill 独立链接）",
    "codex": "分类模式（按目录结构链接）",
    "hermes": "分类模式（按目录结构链接）",
}
_FLAT_AGENTS = frozenset({"claude"})  # 不支持嵌套目录
_NESTED_AGENTS = frozenset({"codex", "hermes"})  # 支持嵌套目录
_ALL_AGENTS: list[str] = list(_AGENT_DIR)

# 本地 skills/ 在选择器中显示的分类名
_LOCAL_CATEGORY = "内置 Skills"


def scan_local_skills(root: Path) -> list[Path]:
    """扫描 skills/ 目录，返回所有包含 SKILL.md 的子目录路径列表。"""
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(
        [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    )


def scan_external_skills(root: Path) -> dict[str, list[Path]]:
    """扫描 external-skills/ 目录，返回 {category_name: [skill_dirs]} 映射。

    仅包含含有 SKILL.md 子目录的分类。
    """
    ext_dir = root / "external-skills"
    if not ext_dir.is_dir():
        return {}
    result: dict[str, list[Path]] = {}
    for cat_dir in sorted(ext_dir.iterdir()):
        if not cat_dir.is_dir():
            continue
        skill_dirs = sorted(
            [d for d in cat_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
        )
        if skill_dirs:
            result[cat_dir.name] = skill_dirs
    return result


# ---------------------------------------------------------------------------
# Curses TUI 分类选择
# ---------------------------------------------------------------------------


def _run_curses_selector(
    categories: dict[str, list[Path]],
    pre_selected: set[str] | None = None,
) -> list[str] | None:
    """curses TUI：方向键导航、空格切换选中、回车确认、q 取消（返回 None）。"""
    cat_names = list(categories.keys())
    selected = [name in (pre_selected or set()) for name in cat_names]
    cursor = [0]  # 用列表使闭包可写

    def draw(stdscr: "curses._CursesWindow") -> None:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "选择要安装的外部 Skill 分类（上下键导航，空格切换，回车确认，q 取消）"
        stdscr.addstr(0, 0, title[: w - 1], curses.A_BOLD)
        stdscr.addstr(1, 0, "─" * min(len(title), w - 1))
        for i, name in enumerate(cat_names):
            y = i + 2
            if y >= h - 2:
                break
            prefix = "[x]" if selected[i] else "[ ]"
            line = f"  {prefix} {name}  ({len(categories[name])} 个 skill)"
            attr = curses.A_REVERSE if i == cursor[0] else curses.A_NORMAL
            stdscr.addstr(y, 0, line[: w - 1], attr)
        hint = "a=全选  n=全不选"
        stdscr.addstr(min(len(cat_names) + 2, h - 1), 0, hint[: w - 1])
        stdscr.refresh()

    def run(stdscr: "curses._CursesWindow") -> list[str]:
        curses.curs_set(0)
        while True:
            draw(stdscr)
            key = stdscr.getch()
            if key == curses.KEY_UP:
                cursor[0] = max(0, cursor[0] - 1)
            elif key == curses.KEY_DOWN:
                cursor[0] = min(len(cat_names) - 1, cursor[0] + 1)
            elif key == ord(" "):
                selected[cursor[0]] = not selected[cursor[0]]
            elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
                break
            elif key == ord("q"):
                return None
            elif key == ord("a"):
                for i in range(len(selected)):
                    selected[i] = True
            elif key == ord("n"):
                for i in range(len(selected)):
                    selected[i] = False
        return [cat_names[i] for i, s in enumerate(selected) if s]

    return curses.wrapper(run)


def _select_categories_stdin(
    categories: dict[str, list[Path]],
    pre_selected: set[str] | None = None,
) -> list[str] | None:
    """终端不支持 curses 时的退化方案：stdin 数字选择。"""
    cat_names = list(categories.keys())
    _pre = pre_selected or set()
    print("可用的外部 Skill 分类：")
    for i, name in enumerate(cat_names, 1):
        mark = " [默认选中]" if name in _pre else ""
        print(f"  {i}. {name}  ({len(categories[name])} 个 skill){mark}")
    print(
        "请输入要安装的分类编号（空格分隔，q 取消，直接回车则全不选）：",
        end=" ",
        flush=True,
    )
    raw = input().strip()
    if raw.lower() == "q":
        return None
    if not raw:
        return []
    result: list[str] = []
    for token in raw.split():
        try:
            idx = int(token) - 1
            if 0 <= idx < len(cat_names):
                result.append(cat_names[idx])
        except ValueError:
            pass
    return result


def select_categories(
    categories: dict[str, list[Path]],
    pre_selected: set[str] | None = None,
) -> list[str] | None:
    """交互式选择分类：优先 curses TUI，不支持时退化为 stdin。返回 None 表示取消。"""
    if not categories:
        return []
    try:
        return _run_curses_selector(categories, pre_selected)
    except Exception:
        return _select_categories_stdin(categories, pre_selected)


# ---------------------------------------------------------------------------
# Agent 客户端选择
# ---------------------------------------------------------------------------


def _run_curses_agent_selector(pre_selected: set[str]) -> list[str] | None:
    """curses TUI：选择 Agent 客户端。返回 None 表示取消。"""
    names = _ALL_AGENTS
    selected = [name in pre_selected for name in names]
    cursor = [0]

    def draw(stdscr: "curses._CursesWindow") -> None:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "选择安装目标 Agent 客户端（上下键导航，空格切换，回车确认，q 取消）"
        stdscr.addstr(0, 0, title[: w - 1], curses.A_BOLD)
        stdscr.addstr(1, 0, "─" * min(len(title), w - 1))
        for i, name in enumerate(names):
            y = i + 2
            if y >= h - 2:
                break
            prefix = "[x]" if selected[i] else "[ ]"
            desc = _AGENT_DESC.get(name, "")
            line = f"  {prefix} {name:<8}  {desc}"
            attr = curses.A_REVERSE if i == cursor[0] else curses.A_NORMAL
            stdscr.addstr(y, 0, line[: w - 1], attr)
        stdscr.addstr(min(len(names) + 2, h - 1), 0, "a=全选  n=全不选")
        stdscr.refresh()

    def run(stdscr: "curses._CursesWindow") -> list[str] | None:
        curses.curs_set(0)
        while True:
            draw(stdscr)
            key = stdscr.getch()
            if key == curses.KEY_UP:
                cursor[0] = max(0, cursor[0] - 1)
            elif key == curses.KEY_DOWN:
                cursor[0] = min(len(names) - 1, cursor[0] + 1)
            elif key == ord(" "):
                selected[cursor[0]] = not selected[cursor[0]]
            elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
                break
            elif key == ord("q"):
                return None
            elif key == ord("a"):
                for i in range(len(selected)):
                    selected[i] = True
            elif key == ord("n"):
                for i in range(len(selected)):
                    selected[i] = False
        return [names[i] for i, s in enumerate(selected) if s]

    return curses.wrapper(run)


def _select_agents_stdin(pre_selected: set[str]) -> list[str] | None:
    """stdin 退化方案：数字选择 Agent 客户端。"""
    names = _ALL_AGENTS
    print("选择安装目标 Agent 客户端：")
    for i, name in enumerate(names, 1):
        mark = " [默认选中]" if name in pre_selected else ""
        print(f"  {i}. {name:<8}  {_AGENT_DESC.get(name, '')}{mark}")
    print("请输入编号（空格分隔，q 取消，直接回车则全不选）：", end=" ", flush=True)
    raw = input().strip()
    if raw.lower() == "q":
        return None
    if not raw:
        return []
    result: list[str] = []
    for token in raw.split():
        try:
            idx = int(token) - 1
            if 0 <= idx < len(names):
                result.append(names[idx])
        except ValueError:
            pass
    return result


def select_agents(pre_selected: set[str] | None = None) -> list[str] | None:
    """交互式选择 Agent 客户端：优先 curses TUI，不支持时退化为 stdin。返回 None 表示取消。"""
    _pre = pre_selected or set()
    try:
        return _run_curses_agent_selector(_pre)
    except Exception:
        return _select_agents_stdin(_pre)


# ---------------------------------------------------------------------------
# 复制与软链接
# ---------------------------------------------------------------------------


def copy_skill(src: Path, target_dir: Path) -> None:
    """将 skill 目录复制到 target_dir/<skill_name>，已存在则覆盖。"""
    dst = target_dir / src.name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(str(src), str(dst))


def install_skills(
    skill_dirs: list[Path],
    target_dir: Path,
    label: str = "",
) -> list[str]:
    """将 skill 列表复制到目标目录，返回失败的 skill 名列表。"""
    failures: list[str] = []
    for skill_dir in skill_dirs:
        display = f"[{label}] {skill_dir.name}" if label else skill_dir.name
        print(f"[INFO] 安装: {display}")
        try:
            copy_skill(skill_dir, target_dir)
        except Exception as exc:
            print(f"[WARN] 安装失败: {skill_dir.name} → {exc}", file=sys.stderr)
            failures.append(skill_dir.name)
    return failures


def create_symlinks(target_dir: Path, symlink_dirs: list[Path]) -> None:
    """为 target_dir 中每个 skill 目录，在各 symlink_dirs 中创建符号链接。

    同名路径（文件、目录或旧链接）已存在时先删除再重建。
    适用于不支持嵌套目录的 agent（如 Claude）。
    """
    if not target_dir.is_dir():
        print(f"[WARN] 目标目录不存在，跳过软链接创建: {target_dir}", file=sys.stderr)
        return
    skill_dirs = sorted([d for d in target_dir.iterdir() if d.is_dir()])
    if not skill_dirs:
        print("[INFO] 目标目录中无 skill，跳过软链接创建")
        return

    for link_parent in symlink_dirs:
        link_parent.mkdir(parents=True, exist_ok=True)
        for skill_dir in skill_dirs:
            link_path = link_parent / skill_dir.name
            if link_path.exists() or link_path.is_symlink():
                if link_path.is_symlink() or link_path.is_file():
                    link_path.unlink()
                else:
                    shutil.rmtree(link_path)
            os.symlink(str(skill_dir.resolve()), str(link_path))
            print(f"[LINK] {link_path} → {skill_dir.resolve()}")


def create_category_symlinks(
    external_cat_dirs: list[Path],
    local_skill_dirs: list[Path],
    symlink_dirs: list[Path],
) -> None:
    """为支持嵌套目录的 agent（Codex/Hermes）创建软链接。

    外部 skill 按选中的分类目录整体软链接，本地 skill 逐个软链接。
    """
    if not symlink_dirs:
        return
    for link_parent in symlink_dirs:
        link_parent.mkdir(parents=True, exist_ok=True)
        # 外部 skill：仅链接用户选中的分类目录
        for cat_dir in external_cat_dirs:
            if not cat_dir.is_dir():
                continue
            link_path = link_parent / cat_dir.name
            if link_path.exists() or link_path.is_symlink():
                if link_path.is_symlink() or link_path.is_file():
                    link_path.unlink()
                else:
                    shutil.rmtree(link_path)
            os.symlink(str(cat_dir.resolve()), str(link_path))
            print(f"[LINK] {link_path} → {cat_dir.resolve()}")
        # 本地 skill：逐个链接
        for skill_dir in local_skill_dirs:
            link_path = link_parent / skill_dir.name
            if link_path.exists() or link_path.is_symlink():
                if link_path.is_symlink() or link_path.is_file():
                    link_path.unlink()
                else:
                    shutil.rmtree(link_path)
            os.symlink(str(skill_dir.resolve()), str(link_path))
            print(f"[LINK] {link_path} → {skill_dir.resolve()}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="安装本地 Skill 到 Agent 目录并创建软链接",
    )
    parser.add_argument(
        "--target",
        default=str(DEFAULT_TARGET),
        help=f"安装目标目录（默认：{DEFAULT_TARGET}）",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="跳过交互式选择，安装所有外部 skill 分类",
    )
    parser.add_argument(
        "--category",
        help="安装指定外部 skill 分类名称（与 --no-interactive 互斥）",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    target_dir = Path(args.target).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: 扫描本地 skills/
    local_skills = scan_local_skills(ROOT)
    print(f"[INFO] 找到本地 skill: {len(local_skills)} 个")

    # Step 2: 扫描 external-skills/
    external_categories = scan_external_skills(ROOT)
    print(f"[INFO] 找到外部 skill 分类: {len(external_categories)} 个")

    # Step 2b: 若无外部 skill，自动调用 download.py 下载
    if not external_categories:
        print("[INFO] 未找到外部 skill，正在自动下载...")
        download_script = ROOT / "scripts" / "download.py"
        result = subprocess.run([sys.executable, str(download_script)])
        if result.returncode != 0:
            print("[WARN] 自动下载失败，继续安装本地 skill", file=sys.stderr)
        else:
            external_categories = scan_external_skills(ROOT)
            print(f"[INFO] 下载后找到外部 skill 分类: {len(external_categories)} 个")

    # Step 3: 决定要安装的分类
    selected_local = False
    selected_categories: list[str] = []
    if args.category:
        # 指定分类：仅安装该外部分类，不含本地 skills
        cat = args.category.strip()
        if cat not in external_categories:
            print(f"[ERROR] 分类不存在或无可用 skill: {cat}", file=sys.stderr)
            return 1
        selected_categories = [cat]
    elif args.no_interactive:
        # 非交互：安装全部（含本地）
        selected_local = bool(local_skills)
        selected_categories = list(external_categories.keys())
    else:
        # 构建统一选择器：本地 skills 排首位，默认勾选
        all_categories: dict[str, list[Path]] = {}
        if local_skills:
            all_categories[_LOCAL_CATEGORY] = local_skills
        all_categories.update(external_categories)
        if all_categories:
            print()
            chosen = select_categories(
                all_categories,
                pre_selected={_LOCAL_CATEGORY} if local_skills else None,
            )
            print()
            if chosen is None:
                print("[INFO] 已取消安装")
                return 0
            selected_local = _LOCAL_CATEGORY in chosen
            selected_categories = [c for c in chosen if c != _LOCAL_CATEGORY]

    # Step 3b: 选择 Agent 客户端
    if args.no_interactive:
        selected_agents = _ALL_AGENTS[:]
    else:
        print()
        result = select_agents(pre_selected=set(_ALL_AGENTS))
        print()
        if result is None:
            print("[INFO] 已取消安装")
            return 0
        selected_agents = result
    flat_dirs = [_AGENT_DIR[a] for a in selected_agents if a in _FLAT_AGENTS]
    nested_dirs = [_AGENT_DIR[a] for a in selected_agents if a in _NESTED_AGENTS]

    # Step 4: 安装本地 skills/
    failures: list[str] = []
    if selected_local:
        failures += install_skills(local_skills, target_dir, label="local")

    # Step 5: 安装选中的外部分类
    for cat_name in selected_categories:
        skill_dirs = external_categories.get(cat_name, [])
        if skill_dirs:
            failures += install_skills(skill_dirs, target_dir, label=cat_name)

    print()

    # Step 6: 创建软链接
    local_to_link = local_skills if selected_local else []
    selected_cat_dirs = [EXTERNAL_SKILLS_DIR / cat for cat in selected_categories]
    if flat_dirs:
        print("[INFO] 创建软链接（Claude 平铺模式）...")
        create_symlinks(target_dir, flat_dirs)
    if nested_dirs:
        print("[INFO] 创建软链接（Codex/Hermes 分类模式）...")
        create_category_symlinks(selected_cat_dirs, local_to_link, nested_dirs)

    print()

    if failures:
        print(f"[ERROR] 以下 skill 安装失败: {', '.join(failures)}", file=sys.stderr)
        return 1

    print(f"[INFO] 安装完成 → {target_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (ValueError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
