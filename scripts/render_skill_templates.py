#!/usr/bin/env python3
"""Render bundled skill templates from a shared source file."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "ros_api" / "skills"
BODY_PATH = SKILLS_DIR / "shared_skill_body.md"

STANDARD_FRONTMATTER = """---
name: ros-api
description: Query academic resources through the ros CLI. Use when the user asks to search papers or ebooks, fetch metadata by DOI or ISBN, query extracted content by SHA256, batch fetch records, inspect scholarly resources in the ROS service, or install and configure the ros CLI.
---
"""

OPENCLAW_FRONTMATTER = """---
name: ros-api
description: Query academic resources through the ros CLI. Use when the user asks to search papers or ebooks, fetch metadata by DOI or ISBN, query extracted content by SHA256, batch fetch records, inspect scholarly resources in the ROS service, or install and configure the ros CLI.
metadata:
  openclaw:
    homepage: https://github.com/Shannon4Science/ros-cli
    requires:
      anyBins:
        - ros
        - python
        - python.exe
---
"""


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"rendered {path.relative_to(ROOT)}")


def main() -> None:
    body = BODY_PATH.read_text(encoding="utf-8").rstrip() + "\n"

    write(SKILLS_DIR / "codex_skill.md", f"{STANDARD_FRONTMATTER}\n{body}")
    write(SKILLS_DIR / "cursor_skill.md", f"{STANDARD_FRONTMATTER}\n{body}")
    write(SKILLS_DIR / "openclaw_skill.md", f"{OPENCLAW_FRONTMATTER}\n{body}")
    write(SKILLS_DIR / "claude_agents.md", body)
    write(ROOT / "AGENTS.md", body)


if __name__ == "__main__":
    main()
