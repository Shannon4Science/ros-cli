# ros CLI

Command-line tool for the ros-api academic resource query service.

## Installation

```bash
pip install git+https://github.com/Shannon4Science/ros-cli.git
```

Or install from local source:

```bash
git clone https://github.com/Shannon4Science/ros-cli.git
cd ros-cli
pip install -e .
```

## Quick Start

```bash
# Configure API Key (interactive)
ros config init

# Search metadata by title
ros metadata query --search "title:machine learning"

# Fetch a paper by DOI
ros metadata fetch --doi "10.1590/1806-9126-rbef-2022-0101"

# Fetch content by SHA256
ros content fetch --sha256 "dee1a64db5c1117b..."
```

## Configuration

Config is stored at `~/.ros/config.json`. You can set it interactively or directly:

```bash
ros config init          # Interactive setup
ros config set-key KEY   # Set API key directly
ros config set-url URL   # Set base URL
ros config show          # Show current config
```

To obtain an API key, visit: https://docs.ros.shlab.tech:18443/concepts/authentication/#get-api-key

## Commands

### Metadata

| Command | Description |
|---------|-------------|
| `ros metadata query` | Search/filter metadata with pagination |
| `ros metadata fetch` | Fetch single metadata by DOI or ISBN |
| `ros metadata batch-fetch` | Batch fetch multiple metadata records |

### Content

| Command | Description |
|---------|-------------|
| `ros content query` | Search/filter content resources |
| `ros content fetch` | Fetch single content by SHA256 |
| `ros content batch-fetch` | Batch fetch multiple content records |

## Output Formats

Use `--output` to control output format:

- `json` (default) - Full JSON output
- `table` - Formatted table using rich
- `compact` - One-line-per-result summary

## Agent Skill Integration

This CLI is designed to be used as a skill by AI coding agents (Cursor, Codex, Claude Code).

### Install skill templates

```bash
ros skill install                     # Auto-detect platform
ros skill install --platform cursor   # Cursor only
ros skill install --platform codex    # Codex only
ros skill install --platform claude   # Claude Code only
ros skill install --platform all      # All platforms
```

Supported platforms and target paths:

| Platform | Target path |
|----------|-------------|
| Cursor | `~/.cursor/skills/ros-api/SKILL.md` |
| Codex | `~/.codex/skills/ros-api/SKILL.md` |
| Claude Code | `./AGENTS.md` (current directory) |

> **Legacy**: `python scripts/install_skills.py` is still available as a compatibility wrapper but calls the same shared module.

### Bundled templates

- `ros_api/skills/cursor_skill.md` — Cursor SKILL.md
- `ros_api/skills/codex_skill.md` — Codex SKILL.md
- `ros_api/skills/claude_agents.md` — Claude Code AGENTS.md
- `AGENTS.md` — Claude Code integration (repo root copy)
