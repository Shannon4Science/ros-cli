"""Install ros-api SKILL.md to Cursor and Codex skill directories."""

import shutil
from pathlib import Path

SKILL_SRC = Path(__file__).resolve().parent.parent
CURSOR_SKILL_DIR = Path.home() / ".cursor" / "skills" / "ros-api"
CODEX_SKILL_DIR = Path.home() / ".codex" / "skills" / "ros-api"

TARGETS = [
    (CURSOR_SKILL_DIR, "cursor"),
    (CODEX_SKILL_DIR, "codex"),
]


def install():
    for target_dir, name in TARGETS:
        target_dir.mkdir(parents=True, exist_ok=True)
        src = SKILL_SRC / "skills" / f"{name}_SKILL.md"
        if not src.exists():
            # Fallback: use the already-installed SKILL.md
            existing = target_dir / "SKILL.md"
            if existing.exists():
                print(f"[{name}] SKILL.md already exists at {target_dir}")
                continue
            print(f"[{name}] Warning: source not found at {src}")
            continue
        dst = target_dir / "SKILL.md"
        shutil.copy2(src, dst)
        print(f"[{name}] Installed SKILL.md to {target_dir}")

    print("\nDone. AGENTS.md for Claude Code is at:", SKILL_SRC / "AGENTS.md")


if __name__ == "__main__":
    install()
