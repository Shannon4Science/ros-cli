#!/usr/bin/env python3
"""Zero-dependency skill installer — works without pip-installing ros-cli.

Usage (one-liner):
    curl -sSL https://raw.githubusercontent.com/Shannon4Science/ros-cli/main/scripts/quick_install.py | python3
    curl -sSL https://raw.githubusercontent.com/Shannon4Science/ros-cli/main/scripts/quick_install.py | python3 - --platform cursor

Windows PowerShell:
    irm https://raw.githubusercontent.com/Shannon4Science/ros-cli/main/scripts/quick_install.py | python

With arguments:
    python quick_install.py                     # auto-detect
    python quick_install.py --platform cursor   # Cursor only
    python quick_install.py --platform codex    # Codex only
    python quick_install.py --platform claude   # Claude Code only
    python quick_install.py --platform all      # all platforms
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

REPO = "Shannon4Science/ros-cli"
BRANCH = "main"
BASE_RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"

TEMPLATES = {
    "cursor": {
        "url": f"{BASE_RAW}/ros_api/skills/cursor_skill.md",
        "dest": Path.home() / ".cursor" / "skills" / "ros-api" / "SKILL.md",
    },
    "codex": {
        "url": f"{BASE_RAW}/ros_api/skills/codex_skill.md",
        "dest": Path.home() / ".codex" / "skills" / "ros-api" / "SKILL.md",
    },
    "claude": {
        "url": f"{BASE_RAW}/ros_api/skills/claude_agents.md",
        "dest": Path.cwd() / "AGENTS.md",
    },
}

ALL_PLATFORMS = list(TEMPLATES.keys())


def _detect() -> list[str]:
    home = Path.home()
    out: list[str] = []
    if (home / ".cursor" / "skills").is_dir():
        out.append("cursor")
    if (home / ".codex" / "skills").is_dir():
        out.append("codex")
    out.append("claude")
    return out


def _download(url: str) -> str:
    try:
        with urlopen(url, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except URLError as e:
        print(f"  [error] Failed to download {url}: {e}", file=sys.stderr)
        sys.exit(1)


def _install(platform: str, *, force: bool = False) -> None:
    info = TEMPLATES[platform]
    dest: Path = info["dest"]

    if dest.exists() and not force:
        ans = input(f"  File exists: {dest}\n  Overwrite? [y/N] ").strip().lower()
        if ans not in ("y", "yes"):
            print(f"  Skipped ({platform})")
            return

    print(f"  Downloading {platform} template...")
    content = _download(info["url"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8", newline="\n")
    print(f"  Installed ({platform}): {dest}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install ros skill templates for AI coding agents (no pip install needed)."
    )
    parser.add_argument(
        "--platform",
        choices=ALL_PLATFORMS + ["all"],
        default=None,
        help="Target platform (default: auto-detect).",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing files without prompting.",
    )
    args = parser.parse_args()

    print("=== ros Skill Quick Installer ===\n")

    if args.platform == "all":
        targets = ALL_PLATFORMS
    elif args.platform:
        targets = [args.platform]
    else:
        targets = _detect()
        print(f"  Auto-detected platforms: {', '.join(targets)}\n")

    for p in targets:
        _install(p, force=args.force)

    print("\nDone! To also install the full CLI:")
    print("  pip install git+https://github.com/Shannon4Science/ros-cli.git")
    print("  ros config init")


if __name__ == "__main__":
    main()
