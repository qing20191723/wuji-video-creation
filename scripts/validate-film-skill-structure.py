#!/usr/bin/env python3
"""Validate the repository film Skill package with standard-library checks."""

from __future__ import annotations

import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "skills" / "seedance-film-production"
ENTRYPOINT = SKILL_ROOT / "SKILL.md"
EXPECTED_VERSION = "3.2.0"
MAX_ENTRYPOINT_LINES = 70
MAX_ENTRYPOINT_CHARACTERS = 6000
MAX_MARKDOWN_LINES = 750
MAX_REFERENCE_FILES = 20


def fail(message: str) -> None:
    raise SystemExit(f"Skill structure validation failed: {message}")


def main() -> int:
    required = [
        ENTRYPOINT,
        SKILL_ROOT / "agents" / "openai.yaml",
        SKILL_ROOT / "assets" / "project-state.template.json",
        SKILL_ROOT / "scripts" / "validate_project_state.py",
        SKILL_ROOT / "scripts" / "test_validate_project_state.py",
        SKILL_ROOT / "references" / "narrative-direction.md",
        SKILL_ROOT / "references" / "state-schema.md",
        SKILL_ROOT / "scripts" / "project_state_v2.py",
        SKILL_ROOT / "scripts" / "migrate_project_state.py",
        SKILL_ROOT / "scripts" / "legacy_project_state.py",
        SKILL_ROOT / "scripts" / "fixtures" / "project-state-1.9.json",
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
    if not version or version.group(1).strip() != EXPECTED_VERSION:
        fail(f"metadata.version must be {EXPECTED_VERSION}")
    if "## When to Use" not in body:
        fail("SKILL.md must contain a When to Use section")
    if len(text.splitlines()) > MAX_ENTRYPOINT_LINES:
        fail(f"SKILL.md exceeds {MAX_ENTRYPOINT_LINES} lines")
    if len(text) > MAX_ENTRYPOINT_CHARACTERS:
        fail(f"SKILL.md exceeds {MAX_ENTRYPOINT_CHARACTERS} characters")

    stage_markers = ("script", "shot_plan", "assets", "storyboard", "compile")
    if any(marker not in body for marker in stage_markers):
        fail("missing stage routes")
    if "references/narrative-direction.md" not in body:
        fail("SKILL.md must route narrative direction to narrative-direction.md")

    routed_refs = set(re.findall(r"\((references/[^)#]+\.md)\)", body))
    missing_refs = [reference for reference in sorted(routed_refs) if not (SKILL_ROOT / reference).is_file()]
    if missing_refs:
        fail("missing routed references: " + ", ".join(missing_refs))

    markdown_paths = sorted(SKILL_ROOT.rglob("*.md"))
    reference_count = len(list((SKILL_ROOT / "references").glob("*.md")))
    if reference_count > MAX_REFERENCE_FILES:
        fail(f"reference file count exceeds {MAX_REFERENCE_FILES} ({reference_count})")
    markdown_lines = sum(
        sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        for path in markdown_paths
    )
    if markdown_lines > MAX_MARKDOWN_LINES:
        fail(f"Markdown package exceeds {MAX_MARKDOWN_LINES} nonblank instruction lines ({markdown_lines})")

    link_pattern = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)")
    broken_links: list[str] = []
    for path in markdown_paths:
        document = path.read_text(encoding="utf-8")
        for target in link_pattern.findall(document):
            if re.match(r"^[a-z]+://", target, re.IGNORECASE):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.is_file():
                broken_links.append(
                    f"{path.relative_to(SKILL_ROOT)} -> {target}"
                )
    if broken_links:
        fail("broken Markdown links: " + ", ".join(sorted(broken_links)))

    rule_owners: dict[str, Path] = {}
    duplicate_rules: list[str] = []
    rule_signal = re.compile(r"必须|不得|禁止|不能|只允许|只负责|需要")
    for path in markdown_paths:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", raw_line).strip()
            normalized = re.sub(r"\s+", " ", line)
            if len(normalized) < 45 or not rule_signal.search(normalized):
                continue
            owner = rule_owners.setdefault(normalized, path)
            if owner != path:
                duplicate_rules.append(
                    f"{owner.relative_to(SKILL_ROOT)} = {path.relative_to(SKILL_ROOT)}: {normalized}"
                )
    if duplicate_rules:
        fail("duplicated hard-rule text: " + " | ".join(duplicate_rules))

    unfinished = re.compile(r"\b(?:TODO|FIXME|PLACEHOLDER)\b|\[TODO\]", re.IGNORECASE)
    for path in SKILL_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".py", ".yaml", ".json"}:
            if unfinished.search(path.read_text(encoding="utf-8")):
                fail(f"unfinished scaffold marker in {path.relative_to(REPOSITORY_ROOT)}")

    print(
        f"Skill structure valid: version {EXPECTED_VERSION}, {len(routed_refs)} routed references, "
        f"{markdown_lines} nonblank Markdown instruction lines, "
        f"{sum(1 for path in SKILL_ROOT.rglob('*') if path.is_file() and '__pycache__' not in path.parts)} files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
