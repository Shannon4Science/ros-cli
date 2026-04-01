"""Thin wrapper around ros_api.skill_install for backward compatibility.

Preferred entry point: ``ros skill install``
"""

from ros_api.skill_install import install

if __name__ == "__main__":
    install(overwrite_ok=False)
