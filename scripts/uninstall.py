#!/usr/bin/env python3
"""卸载脚本：install.py 的反向操作，从 ~/.agents/skills/ 和各 agent 目录移除 skill。

用法：
  python3 scripts/uninstall.py --skill chrome-devtools   # 卸载单个 skill
  python3 scripts/uninstall.py --category Design         # 卸载整个分类（含 Codex/Hermes 分类链接）
  python3 scripts/uninstall.py --all                     # 卸载全部已安装内容
  python3 scripts/uninstall.py --category Web --dry-run  # 预览操作，不实际执行
"""

from __future__ import annotations

import argparse
import curses
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL_SKILLS_DIR = ROOT / "skills"
EXTERNAL_SKILLS_DIR = ROOT / "external-skills"

DEFAULT_TARGET = Path.home() / ".agents" / "skills"
# Agent 目标目录及模式配置（与 install.py 保持一致）
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
_FLAT_AGENTS = frozenset({"claude"})
_NESTED_AGENTS = frozenset({"codex", "hermes"})
_ALL_AGENTS: list[str] = list(_AGENT_DIR)
_LOCAL_CATEGORY = "内置 Skills"


def load_index(root: Path) -> dict:
    index_path = root / "index.json"
    if not index_path.is_file():
        raise ValueError(f"未找到 index.json: {index_path}")
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("categories"), list):
        raise ValueError("index.json 格式错误: categories 必须是数组")
    return payload


def get_category_skill_ids(payload: dict, category_name: str) -> list[str]:
    """从 index.json 查找指定分类的所有 skill id。"""
    for category in payload["categories"]:
        if str(category.get("name", "")).strip() == category_name:
            return [
                str(item.get("id", "")).strip()
                for item in category.get("items", [])
                if item.get("id")
            ]
    raise ValueError(f"未找到分类: {category_name}")


def is_local_skill(skill_id: str) -> bool:
    return (LOCAL_SKILLS_DIR / skill_id / "SKILL.md").exists()


def scan_local_skills(root: Path) -> list[Path]:
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(
        [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    )


def scan_external_skills(root: Path) -> dict[str, list[Path]]:
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
# 分类选择器
# ---------------------------------------------------------------------------


def _run_curses_selector(
    categories: dict[str, list[Path]],
    pre_selected: set[str] | None = None,
) -> list[str] | None:
    """curses TUI：选择要卸载的分类。返回 None 表示取消。"""
    cat_names = list(categories.keys())
    selected = [name in (pre_selected or set()) for name in cat_names]
    cursor = [0]

    def draw(stdscr: "curses._CursesWindow") -> None:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "选择要卸载的 Skill 分类（上下键导航，空格切换，回车确认，q 取消）"
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
        stdscr.addstr(min(len(cat_names) + 2, h - 1), 0, "a=全选  n=全不选")
        stdscr.refresh()

    def run(stdscr: "curses._CursesWindow") -> list[str] | None:
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
    cat_names = list(categories.keys())
    _pre = pre_selected or set()
    print("可用的 Skill 分类：")
    for i, name in enumerate(cat_names, 1):
        mark = " [默认选中]" if name in _pre else ""
        print(f"  {i}. {name}  ({len(categories[name])} 个 skill){mark}")
    print(
        "请输入要卸载的分类编号（空格分隔，q 取消，直接回车则全不选）：",
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
        title = "选择要卸载的 Agent 客户端（上下键导航，空格切换，回车确认，q 取消）"
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

    def run(stdscr: "curses._CursesWindow") -> list[str]:
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
    print("选择要卸载的 Agent 客户端：")
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
# 卸载操作
# ---------------------------------------------------------------------------


def _remove_path(path: Path, dry_run: bool) -> None:
    if not path.exists() and not path.is_symlink():
        return
    verb = "[DRY]" if dry_run else "[INFO]"
    print(f"{verb} 移除: {path}")
    if dry_run:
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)


def do_remove_skill(
    skill_id: str,
    target_dir: Path,
    flat_dirs: list[Path],
    nested_dirs: list[Path],
    dry_run: bool,
) -> None:
    """卸载单个 skill：从 target_dir 和各 agent 目录移除。"""
    _remove_path(target_dir / skill_id, dry_run)
    for link_parent in flat_dirs:
        _remove_path(link_parent / skill_id, dry_run)
    if is_local_skill(skill_id):
        for link_parent in nested_dirs:
            _remove_path(link_parent / skill_id, dry_run)
    elif nested_dirs:
        print(
            f"[WARN] {skill_id} 是外部 skill，Codex/Hermes 通过分类目录链接访问，"
            "如需完全移除请使用 --category",
            file=sys.stderr,
        )


def do_remove_category(
    category_name: str,
    skill_ids: list[str],
    target_dir: Path,
    flat_dirs: list[Path],
    nested_dirs: list[Path],
    dry_run: bool,
) -> None:
    """卸载整个分类：各 skill 从 target_dir 和 flat 目录移除，nested 目录移除分类链接。"""
    for skill_id in skill_ids:
        _remove_path(target_dir / skill_id, dry_run)
        for link_parent in flat_dirs:
            _remove_path(link_parent / skill_id, dry_run)
    for link_parent in nested_dirs:
        _remove_path(link_parent / category_name, dry_run)


def do_remove_all(
    target_dir: Path,
    flat_dirs: list[Path],
    nested_dirs: list[Path],
    dry_run: bool,
) -> None:
    """移除全部已安装内容。"""
    for d in [target_dir, *flat_dirs, *nested_dirs]:
        if d.is_dir():
            for item in sorted(d.iterdir()):
                _remove_path(item, dry_run)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="卸载已安装的 skill（install.py 的反向操作）",
    )
    parser.add_argument(
        "--target",
        default=str(DEFAULT_TARGET),
        help=f"安装目标目录（默认：{DEFAULT_TARGET}）",
    )
    parser.add_argument("--skill", help="卸载单个 skill id")
    parser.add_argument("--category", help="卸载指定分类下全部 skill")
    parser.add_argument(
        "--all", dest="all", action="store_true", help="卸载全部已安装内容"
    )
    parser.add_argument("--dry-run", action="store_true", help="仅打印操作，不实际执行")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    specified = sum([bool(args.skill), bool(args.category), args.all])
    if specified > 1:
        raise ValueError("--skill、--category、--all 最多指定一个")

    target_dir = Path(args.target).expanduser().resolve()

    if args.dry_run:
        print("[INFO] --dry-run 模式，仅打印操作，不实际执行")

    payload = load_index(ROOT)

    if specified == 0:
        # 交互模式：选择分类 → 选择 Agent → 执行卸载
        local_skills = scan_local_skills(ROOT)
        external_categories = scan_external_skills(ROOT)

        all_categories: dict[str, list[Path]] = {}
        if local_skills:
            all_categories[_LOCAL_CATEGORY] = local_skills
        all_categories.update(external_categories)

        if not all_categories:
            print("[INFO] 无可用 skill 分类")
            return 0

        print()
        chosen = select_categories(
            all_categories,
            pre_selected=set(all_categories.keys()),
        )
        print()
        if chosen is None:
            print("[INFO] 已取消卸载")
            return 0
        selected_local = _LOCAL_CATEGORY in chosen
        selected_categories = [c for c in chosen if c != _LOCAL_CATEGORY]

        print()
        result = select_agents(pre_selected=set(_ALL_AGENTS))
        print()
        if result is None:
            print("[INFO] 已取消卸载")
            return 0
        selected_agents = result
        flat_dirs = [_AGENT_DIR[a] for a in selected_agents if a in _FLAT_AGENTS]
        nested_dirs = [_AGENT_DIR[a] for a in selected_agents if a in _NESTED_AGENTS]

        if selected_local:
            for skill_dir in local_skills:
                do_remove_skill(
                    skill_dir.name, target_dir, flat_dirs, nested_dirs, args.dry_run
                )
        for cat_name in selected_categories:
            skill_ids = get_category_skill_ids(payload, cat_name)
            do_remove_category(
                cat_name, skill_ids, target_dir, flat_dirs, nested_dirs, args.dry_run
            )

    else:
        # CLI 模式（指定了 --skill / --category / --all）：选择 Agent → 执行
        print()
        result = select_agents(pre_selected=set(_ALL_AGENTS))
        print()
        if result is None:
            print("[INFO] 已取消卸载")
            return 0
        selected_agents = result
        flat_dirs = [_AGENT_DIR[a] for a in selected_agents if a in _FLAT_AGENTS]
        nested_dirs = [_AGENT_DIR[a] for a in selected_agents if a in _NESTED_AGENTS]

        if args.skill:
            do_remove_skill(
                args.skill.strip(), target_dir, flat_dirs, nested_dirs, args.dry_run
            )
        elif args.category:
            cat = args.category.strip()
            skill_ids = get_category_skill_ids(payload, cat)
            do_remove_category(
                cat, skill_ids, target_dir, flat_dirs, nested_dirs, args.dry_run
            )
        else:
            do_remove_all(target_dir, flat_dirs, nested_dirs, args.dry_run)

    print("[INFO] 卸载完成" if not args.dry_run else "[INFO] dry-run 完成")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (ValueError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
