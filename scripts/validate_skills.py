#!/usr/bin/env python3
"""Validate basic Agent Skill repository structure."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def parse_simple_frontmatter(text: str, path: Path) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path}: missing YAML frontmatter")

    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith(" ") or line.startswith("  "):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata


def main() -> int:
    errors: list[str] = []
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if not skill_files:
        errors.append("No skills/*/SKILL.md files found")

    for skill_file in skill_files:
        skill_dir = skill_file.parent
        try:
            metadata = parse_simple_frontmatter(skill_file.read_text(encoding="utf-8"), skill_file)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        name = metadata.get("name")
        description = metadata.get("description")
        if not name:
            errors.append(f"{skill_file}: missing name")
        elif name != skill_dir.name:
            errors.append(f"{skill_file}: name {name!r} does not match directory {skill_dir.name!r}")
        if not description:
            errors.append(f"{skill_file}: missing description")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"Validated {len(skill_files)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
