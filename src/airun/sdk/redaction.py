"""Privacy and redaction engine for sanitizing traces and metadata."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Set

from airun.config import get_config

# Patterns for catching secret tokens in strings
AUTH_HEADER_PATTERN = re.compile(
    r"(Bearer|Token|Basic|Key)\s+([A-Za-z0-9_\-\.]{6,})", re.IGNORECASE
)
API_KEY_PATTERN = re.compile(r"(sk-[A-Za-z0-9_\-]{10,}|key-[A-Za-z0-9_\-]{10,})", re.IGNORECASE)


def redact_string(val: str) -> str:
    """Redact known secret patterns inside strings."""
    if not isinstance(val, str):
        return val
    val = AUTH_HEADER_PATTERN.sub(r"\1 [REDACTED]", val)
    val = API_KEY_PATTERN.sub(r"[REDACTED_API_KEY]", val)
    return val


def redact_data(data: Any, redact_keys: Optional[Set[str]] = None) -> Any:
    """Recursively sanitize and redact sensitive dictionary keys, headers, and values."""
    if redact_keys is None:
        config = get_config()
        redact_keys = {k.lower() for k in config.privacy.redact_fields}

    if isinstance(data, dict):
        sanitized: Dict[str, Any] = {}
        for k, v in data.items():
            k_str = str(k).lower()
            if any(target in k_str for target in redact_keys):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = redact_data(v, redact_keys)
        return sanitized
    elif isinstance(data, list):
        return [redact_data(item, redact_keys) for item in data]
    elif isinstance(data, tuple):
        return tuple(redact_data(item, redact_keys) for item in data)
    elif isinstance(data, str):
        return redact_string(data)
    else:
        return data


def filter_content(
    content: Any,
    is_prompt: bool = False,
    is_completion: bool = False,
    is_tool_input: bool = False,
    is_tool_output: bool = False,
) -> Any:
    """Check privacy configuration before allowing payload content to be stored."""
    config = get_config()
    if is_prompt and not config.privacy.capture_prompt_content:
        return None
    if is_completion and not config.privacy.capture_completion_content:
        return None
    if is_tool_input and not config.privacy.capture_tool_inputs:
        return None
    if is_tool_output and not config.privacy.capture_tool_outputs:
        return None

    return redact_data(content)
