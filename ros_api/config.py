"""Configuration management for ros CLI.

Stores config at ~/.ros/config.json with api_key and base_url.
"""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_BASE_URL = "https://ros-api.ros.shlab.tech:18443"
CONFIG_DIR = Path.home() / ".ros"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _ensure_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load() -> dict:
    """Load config from disk. Returns empty dict if not found."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save(cfg: dict):
    """Save config dict to disk."""
    _ensure_dir()
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


def get_api_key() -> str | None:
    return load().get("api_key")


def get_base_url() -> str:
    return load().get("base_url", DEFAULT_BASE_URL)


def set_api_key(key: str):
    cfg = load()
    cfg["api_key"] = key
    save(cfg)


def set_base_url(url: str):
    cfg = load()
    cfg["base_url"] = url.rstrip("/")
    save(cfg)


def mask_key(key: str | None) -> str:
    if not key:
        return "(not set)"
    if len(key) <= 8:
        return key[:2] + "***"
    return key[:4] + "***" + key[-4:]
