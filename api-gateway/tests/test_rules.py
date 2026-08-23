import pytest

from app.rules import scan_text

_FAKE_AWS_KEY = "AKIAIOSFODNN7EXAMPLE"  # pragma: allowlist secret
_FAKE_OPENAI_KEY = "sk-abcdefghijklmnopqrstuvwxyz123456"  # pragma: allowlist secret

# (text, expected_rule_or_None)
CASES = [
    (f"here is {_FAKE_AWS_KEY} ok", "aws_access_key"),
    (f"key: {_FAKE_OPENAI_KEY}", "openai_api_key"),
    ("-----BEGIN RSA PRIVATE KEY-----", "private_key_block"),
    ("my id is 44051401359", "pesel"),
    ("number 44051401358 here", None),  # bad checksum
    ("What is the capital of France?", None),
    # case sensitivity (6a): a recased credential is still caught.
    (f"here is {_FAKE_AWS_KEY.lower()} ok", "aws_access_key"),
    # anchoring (6b): a credential glued to a preceding word character is
    # no longer hidden from detection by the leading boundary.
    (f"prefix{_FAKE_AWS_KEY}", "aws_access_key"),
    # separators (6d): a PESEL split by a single hyphen is still caught.
    ("440514-01359", "pesel"),
    ("440514 01359", "pesel"),
    # PESEL false positives (6c): a plausible 11-digit phone number whose
    # month field (digits[2:4] % 20) falls outside 1-12 is not flagged.
    ("48771378733", None),
]


@pytest.mark.parametrize("text,expected_rule", CASES)
def test_scan_text(text, expected_rule):
    match = scan_text(text)
    if expected_rule is None:
        assert match is None
    else:
        assert match is not None
        assert match.rule == expected_rule
