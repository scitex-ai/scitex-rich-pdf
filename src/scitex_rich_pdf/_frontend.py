"""Locate the assets of the framework-neutral Rich PDF component."""

from __future__ import annotations

from pathlib import Path


def get_frontend_package_dir() -> Path:
    """Return the installed directory usable as an npm file dependency."""
    return Path(__file__).resolve().parent / "frontend"
