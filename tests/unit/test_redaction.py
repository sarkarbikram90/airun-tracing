"""Unit tests for privacy and sensitive data redaction."""

from airun.sdk.redaction import redact_data, redact_string


def test_redact_string_bearer_token():
    text = "Authorization: Bearer sk-1234567890abcdef"
    redacted = redact_string(text)
    assert "sk-1234567890abcdef" not in redacted
    assert "[REDACTED]" in redacted


def test_redact_dict_sensitive_keys():
    data = {
        "user": "alice",
        "api_key": "secret-key-123456",
        "nested": {
            "token": "tok_abcdef",
            "safe_param": 42,
        },
        "list_items": [
            {"password": "mypassword"},
            {"data": "clean_value"},
        ],
    }

    sanitized = redact_data(data)
    assert sanitized["user"] == "alice"
    assert sanitized["api_key"] == "[REDACTED]"
    assert sanitized["nested"]["token"] == "[REDACTED]"
    assert sanitized["nested"]["safe_param"] == 42
    assert sanitized["list_items"][0]["password"] == "[REDACTED]"
    assert sanitized["list_items"][1]["data"] == "clean_value"
