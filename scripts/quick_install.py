#!/usr/bin/env python3
"""Zero-dependency installer for ros skill templates only.

This script does not install the ros CLI itself.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
from urllib.error import URLError
from urllib.request import urlopen

REPO = "Shannon4Science/ros-cli"
BRANCH = "main"
BASE_RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
LOCAL_ROOT = Path(__file__).resolve().parents[1]

TEMPLATES = {
    "cursor": {
        "url": f"{BASE_RAW}/ros_api/skills/cursor_skill.md",
        "dest": Path.home() / ".cursor" / "skills" / "ros-api" / "SKILL.md",
        "path": LOCAL_ROOT / "ros_api" / "skills" / "cursor_skill.md",
    },
    "codex": {
        "url": f"{BASE_RAW}/ros_api/skills/codex_skill.md",
        "dest": Path.home() / ".codex" / "skills" / "ros-api" / "SKILL.md",
        "path": LOCAL_ROOT / "ros_api" / "skills" / "codex_skill.md",
    },
    "openclaw": {
        "url": f"{BASE_RAW}/ros_api/skills/openclaw_skill.md",
        "dest": Path.home() / ".openclaw" / "skills" / "ros-api" / "SKILL.md",
        "path": LOCAL_ROOT / "ros_api" / "skills" / "openclaw_skill.md",
    },
    "claude": {
        "url": f"{BASE_RAW}/ros_api/skills/claude_agents.md",
        "dest": Path.cwd() / "AGENTS.md",
        "path": LOCAL_ROOT / "ros_api" / "skills" / "claude_agents.md",
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
    if (home / ".openclaw").is_dir() or shutil.which("openclaw"):
        out.append("openclaw")
    out.append("claude")
    return out


def _download(url: str) -> str:
    try:
        with urlopen(url, timeout=30) as response:
            return response.read().decode("utf-8")
    except URLError as exc:
        print(f"  [error] Failed to download {url}: {exc}", file=sys.stderr)
        sys.exit(1)


def _install(platform: str, *, force: bool = False) -> None:
    info = TEMPLATES[platform]
    dest: Path = info["dest"]

    if dest.exists() and not force:
        answer = input(f"  File exists: {dest}\n  Overwrite? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print(f"  Skipped ({platform})")
            return

    local_template = info["path"]
    if local_template.exists():
        print(f"  Using local {platform} template...")
        content = local_template.read_text(encoding="utf-8")
    else:
        print(f"  Downloading {platform} template...")
        content = _download(info["url"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8", newline="\n")
    print(f"  Installed ({platform}): {dest}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install ros skill templates for AI coding agents. This does not install the ros CLI."
    )
    parser.add_argument(
        "--platform",
        choices=ALL_PLATFORMS + ["all"],
        default=None,
        help="Target platform (default: auto-detect).",
    )
    parser.add_argument(
        "--force",
        "-f",
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

    for platform in targets:
        _install(platform, force=args.force)

    print("\nSkill templates installed.")
    print("Before using the skill, install and configure the CLI:")
    print("  pip install --upgrade git+https://github.com/Shannon4Science/ros-cli.git")
    print("  ros config init")


if __name__ == "__main__":
    main()
