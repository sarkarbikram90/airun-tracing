"""Configuration loader for airun."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field


class PrivacyConfig(BaseModel):
    capture_prompt_content: bool = False
    capture_completion_content: bool = False
    capture_tool_inputs: bool = False
    capture_tool_outputs: bool = False
    redact_fields: List[str] = Field(
        default_factory=lambda: [
            "api_key",
            "authorization",
            "token",
            "password",
            "secret",
            "bearer",
            "client_secret",
            "private_key",
        ]
    )


class AirunConfig(BaseModel):
    storage_backend: str = "sqlite"  # "sqlite" or "jsonl"
    storage_dir: Path = Field(default_factory=lambda: Path(".airun/traces"))
    sqlite_path: Path = Field(default_factory=lambda: Path(".airun/traces.db"))
    pricing_file: Optional[Path] = None
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig)


_DEFAULT_CONFIG: Optional[AirunConfig] = None


def get_config_path(search_cwd: bool = True) -> Optional[Path]:
    """Find configuration file in current directory or user home."""
    if search_cwd:
        cwd_config = Path.cwd() / ".airun" / "config.yaml"
        if cwd_config.exists():
            return cwd_config

    home_config = Path.home() / ".airun" / "config.yaml"
    if home_config.exists():
        return home_config

    return None


def load_config(config_path: Optional[Path] = None) -> AirunConfig:
    """Load configuration from file or return default configuration."""
    global _DEFAULT_CONFIG
    if config_path is None:
        config_path = get_config_path()

    if config_path and config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            _DEFAULT_CONFIG = AirunConfig(**data)
            return _DEFAULT_CONFIG
        except Exception:
            pass

    _DEFAULT_CONFIG = AirunConfig()
    return _DEFAULT_CONFIG


def get_config() -> AirunConfig:
    """Return currently active configuration singleton."""
    global _DEFAULT_CONFIG
    if _DEFAULT_CONFIG is None:
        _DEFAULT_CONFIG = load_config()
    return _DEFAULT_CONFIG
