#!/usr/bin/env python3
"""Validate the repository film Skill package with standard-library checks."""

from __future__ import annotations

import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "skills" / "seedance-film-production"
ENTRYPOINT = SKILL_ROOT / "SKILL.md"


def fail(message: str) -> None:
    raise SystemExit(f"Skill structure validation failed: {message}")


def main() -> int:
    required = [
        ENTRYPOINT,
        SKILL_ROOT / "agents" / "openai.yaml",
        SKILL_ROOT / "assets" / "project-state.template.json",
        SKILL_ROOT / "scripts" / "validate_project_state.py",
        SKILL_ROOT / "scripts" / "test_validate_project_state.py",
    ]
    missing = [str(path.relative_to(REPOSITORY_ROOT)) for path in required if not path.is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    text = ENTRYPOINT.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    try:
        frontmatter, body = text[4:].split("\n---\n", 1)
    except ValueError:
        fail("SKILL.md frontmatter is not closed")

    name = re.search(r"(?m)^name:\s*([^\n]+)$", frontmatter)
    description = re.search(r"(?m)^description:\s*([^\n]+)$", frontmatter)
    version = re.search(r'(?m)^\s{2}version:\s*["\']?([^"\'\n]+)', frontmatter)
    if not name or name.group(1).strip() != "seedance-film-production":
        fail("frontmatter name must be seedance-film-production")
    if not description or not description.group(1).strip():
        fail("frontmatter description is required")
    if len(description.group(1).strip()) > 240:
        fail("frontmatter description is too broad; keep it under 240 characters")
    if not version or version.group(1).strip() != "1.7.0":
        fail("metadata.version must be 1.7.0")
    if "## When to Use" not in body:
        fail("SKILL.md must contain a When to Use section")

    routed_refs = set(re.findall(r"\((references/[^)#]+\.md)\)", body))
    missing_refs = [reference for reference in sorted(routed_refs) if not (SKILL_ROOT / reference).is_file()]
    if missing_refs:
        fail("missing routed references: " + ", ".join(missing_refs))

    unfinished = re.compile(r"\b(?:TODO|FIXME|PLACEHOLDER)\b|\[TODO\]", re.IGNORECASE)
    for path in SKILL_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".py", ".yaml", ".json"}:
            if unfinished.search(path.read_text(encoding="utf-8")):
                fail(f"unfinished scaffold marker in {path.relative_to(REPOSITORY_ROOT)}")

    print(
        f"Skill structure valid: version 1.7.0, {len(routed_refs)} routed references, "
        f"{sum(1 for path in SKILL_ROOT.rglob('*') if path.is_file() and '__pycache__' not in path.parts)} files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
