"""Configuration loading and project-relative path resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load the project configuration."""
    config_path = path or PROJECT_ROOT / "config" / "project.yaml"
    with config_path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def project_path(value: str | Path) -> Path:
    """Resolve a configured path relative to the repository root."""
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path
