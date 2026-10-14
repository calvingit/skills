#!/usr/bin/env python3
"""Static checks for this skills repository.

Checks local Markdown links and anchors, SKILL.md frontmatter, and
agents/openai.yaml basics, then runs engineering/shared/check.py.
Usage: python3 scripts/check_repo.py [--no-state-tests]
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIRS = ("engineering", "backend", "documents", "work")
# Example paths inside templates, not real links.
IGNORED_LINKS = {
    ("engineering/project-setup/references/profile.md", ".agents/engineering-profile.md"),
    ("engineering/solution-design/references/hld-template.md", "SPEC.md"),
}


def slug(heading):
    h = re.sub(r"`", "", heading.strip().lower())
    h = re.sub(r"[^\w\- \u4e00-\u9fff]", "", h)
    return h.replace(" ", "-")


def anchors(path):
    text = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
    return {slug(h) for h in re.findall(r"^#+\s+(.*)$", text, re.M)}


def tracked_markdown():
    out = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"], cwd=ROOT, text=True)
    return [ROOT / p for p in out.split() if (ROOT / p).exists()]


def check_links():
    errors = []
    for md in tracked_markdown():
        rel = md.relative_to(ROOT).as_posix()
        text = re.sub(r"```.*?```", "", md.read_text(), flags=re.S)
        for url in re.findall(r"\]\(([^)\s]+)\)", text):
            if re.match(r"[a-z][a-z0-9+.-]*:", url) or (rel, url) in IGNORED_LINKS:
                continue
            path, _, anchor = url.partition("#")
            target = (md.parent / path).resolve() if path else md
            if not target.exists():
                errors.append(f"{rel}: missing target {url}")
            elif anchor and target.suffix == ".md" and anchor.lower() not in anchors(target):
                errors.append(f"{rel}: missing anchor {url}")
    return errors


def check_skills():
    errors = []
    for top in SKILL_DIRS:
        for skill in sorted((ROOT / top).glob("*/SKILL.md")):
            rel = skill.relative_to(ROOT).as_posix()
            m = re.match(r"---\n(.*?)\n---\n", skill.read_text(), re.S)
            if not m:
                errors.append(f"{rel}: missing frontmatter")
                continue
            fields = dict(re.findall(r"^(\w[\w-]*):\s*(.*)$", m.group(1), re.M))
            if fields.get("name") != skill.parent.name:
                errors.append(f"{rel}: name {fields.get('name')!r} != directory")
            if not fields.get("description", "").strip():
                errors.append(f"{rel}: empty description")
            yaml = skill.parent / "agents/openai.yaml"
            if yaml.exists():
                body = yaml.read_text()
                keys = set(re.findall(r"^(\w+):", body, re.M))
                policy = re.search(r"^\s+allow_implicit_invocation:\s*(\S+)", body, re.M)
                if "\t" in body or not keys or not keys <= {"interface", "policy", "dependencies"}:
                    errors.append(f"{yaml.relative_to(ROOT)}: unexpected top-level keys {sorted(keys)}")
                if policy and policy.group(1) not in ("true", "false"):
                    errors.append(f"{yaml.relative_to(ROOT)}: allow_implicit_invocation must be true or false")
    return errors


def main():
    errors = check_links() + check_skills()
    for e in errors:
        print("FAIL", e)
    print(f"links and skill metadata: {'FAIL' if errors else 'OK'}")
    code = 1 if errors else 0
    if "--no-state-tests" not in sys.argv:
        code |= subprocess.call([sys.executable, str(ROOT / "engineering/shared/check.py")], cwd=ROOT)
    return code


if __name__ == "__main__":
    sys.exit(main())
