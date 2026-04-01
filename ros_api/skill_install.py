"""Shared skill installation logic for AI agent platforms.

Used by both ``ros skill install`` (CLI) and ``scripts/install_skills.py``.
"""

from __future__ import annotations

import sys
from importlib.resources import files
from pathlib import Path
from typing import Callable

ALL_PLATFORMS = ("cursor", "codex", "claude")

TEMPLATE_MAP = {
    "cursor": "cursor_skill.md",
    "codex": "codex_skill.md",
    "claude": "claude_agents.md",
}

DEST_FILENAME = {
    "cursor": "SKILL.md",
    "codex": "SKILL.md",
    "claude": "AGENTS.md",
}


def detected_platforms() -> list[str]:
    """Return platforms whose skill directories already exist on this machine."""
    home = Path.home()
    out: list[str] = []
    if (home / ".cursor" / "skills").is_dir():
        out.append("cursor")
    if (home / ".codex" / "skills").is_dir():
        out.append("codex")
    out.append("claude")
    return out


def _read_template(filename: str) -> str:
    root = files("ros_api.skills")
    return (root / filename).read_text(encoding="utf-8")


def dest_path(platform: str, cwd: Path | None = None) -> Path:
    """Compute destination file path for *platform*."""
    home = Path.home()
    if platform == "cursor":
        return home / ".cursor" / "skills" / "ros-api" / "SKILL.md"
    if platform == "codex":
        return home / ".codex" / "skills" / "ros-api" / "SKILL.md"
    if platform == "claude":
        return (cwd or Path.cwd()) / "AGENTS.md"
    raise ValueError(f"Unknown platform: {platform}")


def install_one(
    platform: str,
    *,
    cwd: Path | None = None,
    overwrite_ok: bool = False,
    confirm: Callable[[str], bool] | None = None,
    echo: Callable[[str], None] | None = None,
) -> bool:
    """Install skill template for a single *platform*.

    Parameters
    ----------
    platform:
        One of ``"cursor"``, ``"codex"``, ``"claude"``.
    cwd:
        Working directory for Claude's ``AGENTS.md`` (defaults to ``Path.cwd()``).
    overwrite_ok:
        If *True*, overwrite existing files without prompting.
    confirm:
        Optional callback ``(message) -> bool`` to ask user before overwriting.
        When *None*, existing files are silently skipped unless *overwrite_ok*.
    echo:
        Optional callback ``(message) -> None`` for output.  Falls back to *print*.

    Returns
    -------
    bool
        *True* if the file was written, *False* if skipped.
    """
    echo = echo or print
    template_name = TEMPLATE_MAP.get(platform)
    if template_name is None:
        echo(f"[error] Unknown platform: {platform}")
        return False

    content = _read_template(template_name)
    dst = dest_path(platform, cwd=cwd)
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists() and not overwrite_ok:
        if confirm:
            if not confirm(f"File exists:\n  {dst}\nOverwrite?"):
                echo(f"Skipped ({platform}): {dst}")
                return False
        else:
            echo(f"Skipped ({platform}): {dst} (already exists)")
            return False

    dst.write_text(content, encoding="utf-8", newline="\n")
    echo(f"Installed ({platform}): {dst}")
    return True


def install(
    platforms: list[str] | None = None,
    *,
    cwd: Path | None = None,
    overwrite_ok: bool = False,
    confirm: Callable[[str], bool] | None = None,
    echo: Callable[[str], None] | None = None,
) -> None:
    """Install skill templates for the given *platforms* (or auto-detect)."""
    if platforms is None:
        platforms = list(ALL_PLATFORMS)
    for p in platforms:
        install_one(p, cwd=cwd, overwrite_ok=overwrite_ok, confirm=confirm, echo=echo)
