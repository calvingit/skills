#!/usr/bin/env python3
"""外部 Skill 下载脚本：从 index.json 读取技能列表，通过 git clone 浅克隆到 .cache/ 目录，
再按分类提取到 external-skills/ 目录。

用法：
  python3 scripts/download.py                    # 下载全部
  python3 scripts/download.py --category Tool    # 仅下载 Tool 分类
  python3 scripts/download.py --clean-cache      # 清理 .cache/ 后重新下载
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "index.json"
CACHE_DIR = ROOT / ".cache"
EXTERNAL_SKILLS_DIR = ROOT / "external-skills"

# 匹配 GitHub URL：
#   https://github.com/<owner>/<repo>
#   https://github.com/<owner>/<repo>/tree/<branch>/<subpath>
_GITHUB_URL_RE = re.compile(
    r"^https://github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/tree/([^/]+)/(.+))?/?$"
)


def parse_skill_url(url: str) -> tuple[str, str, str | None, str | None]:
    """解析 GitHub URL，返回 (owner, repo, branch, subpath)。

    branch 和 subpath 在无子路径时为 None。
    """
    m = _GITHUB_URL_RE.match(url.strip().rstrip("/"))
    if not m:
        raise ValueError(f"无法解析 GitHub URL: {url!r}")
    owner, repo, branch, subpath = m.group(1), m.group(2), m.group(3), m.group(4)
    return owner, repo, branch or None, subpath or None


def make_cache_dir_name(owner: str, repo: str) -> str:
    """生成 .cache 子目录名，格式为 owner-repo。"""
    return f"{owner}-{repo}"


def load_index(root: Path) -> dict:
    """读取并返回 index.json 内容。"""
    index_path = root / "index.json"
    if not index_path.is_file():
        raise ValueError(f"未找到 index.json: {index_path}")
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("categories"), list):
        raise ValueError("index.json 格式错误: categories 必须是数组")
    return payload


def ensure_category_dirs(
    root: Path, payload: dict, category_filter: str | None = None
) -> None:
    """在 external-skills/ 下确保分类子目录存在。"""
    for category in payload["categories"]:
        name = str(category.get("name", "")).strip()
        if not name:
            continue
        if category_filter and name != category_filter:
            continue
        category_dir = root / "external-skills" / name
        category_dir.mkdir(parents=True, exist_ok=True)


def collect_clone_targets(
    payload: dict, category_filter: str | None = None
) -> dict[str, dict[str, str | None]]:
    """收集需要克隆的仓库信息，按 cache_name 去重。

    返回 {cache_name: {owner, repo, branch, url}}。
    """
    targets: dict[str, dict[str, str | None]] = {}
    for category in payload["categories"]:
        name = str(category.get("name", "")).strip()
        if category_filter and name != category_filter:
            continue
        for item in category.get("items", []):
            url = str(item.get("url", "")).strip()
            if not url:
                continue
            try:
                owner, repo, branch, _ = parse_skill_url(url)
            except ValueError as exc:
                print(f"[WARN] 跳过无效 URL: {url} → {exc}", file=sys.stderr)
                continue
            cache_name = make_cache_dir_name(owner, repo)
            if cache_name not in targets:
                targets[cache_name] = {
                    "owner": owner,
                    "repo": repo,
                    "branch": branch,
                    "url": f"https://github.com/{owner}/{repo}.git",
                }
    return targets


def clone_repos(
    cache_dir: Path,
    targets: dict[str, dict[str, str | None]],
) -> list[str]:
    """浅克隆所有目标仓库到 cache_dir，已存在则跳过。返回失败 cache_name 列表。"""
    failures: list[str] = []
    cache_dir.mkdir(parents=True, exist_ok=True)
    for cache_name, info in targets.items():
        dest = cache_dir / cache_name
        if dest.exists():
            print(f"[SKIP] 缓存已存在，跳过克隆: {cache_name}")
            continue
        clone_url = str(info["url"])
        cmd: list[str] = ["git", "clone", "--depth", "1"]
        branch = info.get("branch")
        if branch:
            cmd += ["--branch", branch]
        cmd += [clone_url, str(dest)]
        print(f"[INFO] 克隆仓库: {clone_url}")
        print(f"[CMD]  {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            failures.append(cache_name)
            print(f"[WARN] 克隆失败: {cache_name}", file=sys.stderr)
    return failures


# 单 skill 提取时只复制这些名称的文件/目录
_SKILL_COPY_NAMES = {"SKILL.md", "references", "scripts"}


def _copy_skill_dir(src: Path, dst: Path) -> None:
    """将 src 目录（子路径 skill）复制到 dst，已存在则覆盖，排除 .git 目录。"""
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git"))


def _copy_single_skill(repo_dir: Path, dst: Path) -> None:
    """将单 skill 仓库的必要文件复制到 dst：只取 SKILL.md、references/、scripts/。"""
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for name in _SKILL_COPY_NAMES:
        src_item = repo_dir / name
        if src_item.is_file():
            shutil.copy2(str(src_item), str(dst / name))
        elif src_item.is_dir():
            shutil.copytree(str(src_item), str(dst / name))


def _is_single_skill(repo_dir: Path) -> bool:
    """判断仓库根目录是否是单个 skill（存在 SKILL.md 或 references/ 目录）。

    注意：优先在调用方检查 skills/ 子目录（组合包），此函数不负责该判断。
    """
    if (repo_dir / "SKILL.md").exists():
        return True
    if (repo_dir / "references").is_dir():
        return True
    return False


def extract_skills(
    payload: dict,
    cache_dir: Path,
    external_skills_dir: Path,
    category_filter: str | None = None,
    clone_failures: set[str] | None = None,
) -> list[str]:
    """从 cache 提取 skill 到 external-skills 分类目录，返回失败的 skill id 列表。"""
    failures: list[str] = []
    clone_failures = clone_failures or set()

    for category in payload["categories"]:
        cat_name = str(category.get("name", "")).strip()
        if not cat_name:
            continue
        if category_filter and cat_name != category_filter:
            continue
        cat_dir = external_skills_dir / cat_name

        for item in category.get("items", []):
            skill_id = str(item.get("id", "")).strip()
            url = str(item.get("url", "")).strip()
            if not url or not skill_id:
                continue
            try:
                owner, repo, _, subpath = parse_skill_url(url)
            except ValueError:
                continue

            cache_name = make_cache_dir_name(owner, repo)
            if cache_name in clone_failures:
                print(f"[SKIP] 克隆失败，跳过提取: {skill_id}")
                continue

            repo_dir = cache_dir / cache_name
            if not repo_dir.exists():
                print(
                    f"[WARN] cache 目录不存在，跳过提取: {cache_name}", file=sys.stderr
                )
                failures.append(skill_id)
                continue

            if subpath:
                # 有子路径：直接复制指定子目录，以 id 命名
                src = repo_dir / subpath
                if not src.exists():
                    print(f"[WARN] 子路径不存在: {src}", file=sys.stderr)
                    failures.append(skill_id)
                    continue
                dst = cat_dir / skill_id
                print(f"[INFO] 提取 skill: {skill_id} ← {src}")
                try:
                    _copy_skill_dir(src, dst)
                except Exception as exc:
                    print(f"[WARN] 复制失败: {skill_id} → {exc}", file=sys.stderr)
                    failures.append(skill_id)
            else:
                # 无子路径：优先判断组合包（skills/ 子目录），再判断单 skill
                if (repo_dir / "skills").is_dir():
                    # 组合包：遍历 skills/ 子目录，各自以子目录名存放
                    skills_subdir = repo_dir / "skills"
                    sub_items = sorted(
                        [d for d in skills_subdir.iterdir() if d.is_dir()]
                    )
                    if not sub_items:
                        print(
                            f"[WARN] 组合包的 skills/ 目录为空: {cache_name}",
                            file=sys.stderr,
                        )
                        failures.append(skill_id)
                        continue
                    for sub in sub_items:
                        dst = cat_dir / sub.name
                        print(f"[INFO] 提取组合 skill: {sub.name} ← {cache_name}/skills/{sub.name}")
                        try:
                            _copy_skill_dir(sub, dst)
                        except Exception as exc:
                            print(
                                f"[WARN] 复制失败: {sub.name} → {exc}",
                                file=sys.stderr,
                            )
                            failures.append(sub.name)
                elif _is_single_skill(repo_dir):
                    dst = cat_dir / skill_id
                    print(
                        f"[INFO] 提取单 skill: {skill_id} ← {cache_name}/"
                    )
                    try:
                        _copy_single_skill(repo_dir, dst)
                    except Exception as exc:
                        print(
                            f"[WARN] 复制失败: {skill_id} → {exc}", file=sys.stderr
                        )
                        failures.append(skill_id)
                else:
                    print(
                        f"[WARN] 无法判断 skill 类型，跳过: {skill_id} (url: {url})",
                        file=sys.stderr,
                    )
                    failures.append(skill_id)

    return failures


def create_category_descriptions(
    payload: dict,
    external_skills_dir: Path,
    category_filter: str | None = None,
) -> None:
    """在已提取的分类目录下创建 DESCRIPTION.md 文件。"""
    for category in payload["categories"]:
        name = str(category.get("name", "")).strip()
        if not name:
            continue
        if category_filter and name != category_filter:
            continue
        description = str(category.get("description", "")).strip()
        if not description:
            continue
        cat_dir = external_skills_dir / name
        if not cat_dir.is_dir():
            continue
        desc_file = cat_dir / "DESCRIPTION.md"
        desc_file.write_text(f"---\ndescription: {description}\n---\n", encoding="utf-8")
        print(f"[INFO] 建分类描述: {name}")


def collect_expected_skill_dirs(
    payload: dict,
    cache_dir: Path,
    category_filter: str | None = None,
    clone_failures: set[str] | None = None,
) -> tuple[dict[str, set[str]], set[str]]:
    """收集每个分类期望存在的 skill 目录名。

    返回 (expected_map, unsafe_categories)。
    - expected_map: {分类名: {skill_dir...}}
    - unsafe_categories: 无法可靠推导期望集合的分类，后续应跳过 prune
    """
    clone_failures = clone_failures or set()
    expected: dict[str, set[str]] = {}
    unsafe_categories: set[str] = set()

    for category in payload["categories"]:
        cat_name = str(category.get("name", "")).strip()
        if not cat_name:
            continue
        if category_filter and cat_name != category_filter:
            continue

        expected.setdefault(cat_name, set())

        for item in category.get("items", []):
            skill_id = str(item.get("id", "")).strip()
            url = str(item.get("url", "")).strip()
            if not skill_id or not url:
                continue

            try:
                owner, repo, _, subpath = parse_skill_url(url)
            except ValueError:
                unsafe_categories.add(cat_name)
                continue

            if subpath:
                expected[cat_name].add(skill_id)
                continue

            cache_name = make_cache_dir_name(owner, repo)
            if cache_name in clone_failures:
                unsafe_categories.add(cat_name)
                continue

            repo_dir = cache_dir / cache_name
            if not repo_dir.exists():
                unsafe_categories.add(cat_name)
                continue

            if (repo_dir / "skills").is_dir():
                sub_items = sorted([d for d in (repo_dir / "skills").iterdir() if d.is_dir()])
                if not sub_items:
                    unsafe_categories.add(cat_name)
                    continue
                expected[cat_name].update(sub.name for sub in sub_items)
            elif _is_single_skill(repo_dir):
                expected[cat_name].add(skill_id)
            else:
                unsafe_categories.add(cat_name)

    return expected, unsafe_categories


def prune_external_skills(
    external_skills_dir: Path,
    expected_map: dict[str, set[str]],
    unsafe_categories: set[str],
) -> None:
    """删除 external-skills 中已不在 index.json 期望集合里的旧 skill 目录。"""
    for cat_name, expected_skills in expected_map.items():
        cat_dir = external_skills_dir / cat_name
        if not cat_dir.is_dir():
            continue

        if cat_name in unsafe_categories:
            print(
                f"[WARN] 分类 {cat_name} 无法可靠推导期望 skill 集合，跳过清理",
                file=sys.stderr,
            )
            continue

        current_skill_dirs = {d.name for d in cat_dir.iterdir() if d.is_dir()}
        stale_dirs = sorted(current_skill_dirs - expected_skills)
        for name in stale_dirs:
            stale_path = cat_dir / name
            shutil.rmtree(stale_path)
            print(f"[INFO] 清理过期 skill: {cat_name}/{name}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从 GitHub 下载外部 Skill 到 external-skills/ 目录",
    )
    parser.add_argument("--category", help="仅下载指定分类")
    parser.add_argument(
        "--clean-cache",
        action="store_true",
        help="下载前清理 .cache/ 目录（重新克隆全部仓库）",
    )
    parser.add_argument(
        "--no-prune",
        action="store_true",
        help="不清理 external-skills 中已过期的 skill 目录",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    category_filter: str | None = args.category.strip() if args.category else None

    payload = load_index(ROOT)

    if args.clean_cache and CACHE_DIR.exists():
        print("[INFO] 清理 .cache/ 目录...")
        shutil.rmtree(CACHE_DIR)

    # Step 1: 创建分类目录
    ensure_category_dirs(ROOT, payload, category_filter)

    # Step 2: 收集需要克隆的仓库
    targets = collect_clone_targets(payload, category_filter)
    if not targets:
        print("[INFO] 无需克隆的仓库（分类过滤或 index.json 为空）")
        return 0

    # Step 3: 浅克隆仓库到 .cache/
    clone_failures_list = clone_repos(CACHE_DIR, targets)
    clone_failures = set(clone_failures_list)

    print()

    # Step 4: 从 cache 提取 skill 到 external-skills/
    extract_failures = extract_skills(
        payload,
        CACHE_DIR,
        EXTERNAL_SKILLS_DIR,
        category_filter,
        clone_failures,
    )

    # Step 5: 在分类目录创建 DESCRIPTION.md
    create_category_descriptions(payload, EXTERNAL_SKILLS_DIR, category_filter)

    # Step 6: 清理 external-skills 里已不在 index.json 中的旧 skill 目录
    # 为避免误删，出现克隆/提取异常时跳过 prune。
    if args.no_prune:
        print("[INFO] 已关闭清理（--no-prune）")
    elif clone_failures or extract_failures:
        print("[WARN] 检测到克隆/提取异常，跳过清理过期 skill", file=sys.stderr)
    else:
        expected_map, unsafe_categories = collect_expected_skill_dirs(
            payload,
            CACHE_DIR,
            category_filter,
            clone_failures,
        )
        prune_external_skills(EXTERNAL_SKILLS_DIR, expected_map, unsafe_categories)

    print()

    if clone_failures or extract_failures:
        if clone_failures:
            print(
                f"[ERROR] 克隆失败的仓库: {', '.join(sorted(clone_failures))}",
                file=sys.stderr,
            )
        if extract_failures:
            print(
                f"[ERROR] 提取失败的 skill: {', '.join(extract_failures)}",
                file=sys.stderr,
            )
        return 1

    print("[INFO] 下载完成")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (ValueError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
