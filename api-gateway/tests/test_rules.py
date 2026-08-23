import pytest

from app.rules import scan_text

_FAKE_AWS_KEY = "AKIAIOSFODNN7EXAMPLE"  # pragma: allowlist secret
_FAKE_OPENAI_KEY = "sk-abcdefghijklmnopqrstuvwxyz123456"  # pragma: allowlist secret
_FAKE_PRIVATE_KEY_HEADER = "-----BEGIN RSA PRIVATE KEY-----"  # pragma: allowlist secret
_FAKE_OPENAI_PROJECT_KEY = (
    "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"  # pragma: allowlist secret
)

# (text, expected_rule_or_None)
CASES = [
    (f"here is {_FAKE_AWS_KEY} ok", "aws_access_key"),
    (f"key: {_FAKE_OPENAI_KEY}", "openai_api_key"),
    (_FAKE_PRIVATE_KEY_HEADER, "private_key_block"),
    ("my id is 44051401359", "pesel"),
    ("number 44051401358 here", None),  # bad checksum
    ("What is the capital of France?", None),
    # case sensitivity (6a): a recased credential is still caught.
    (f"here is {_FAKE_AWS_KEY.lower()} ok", "aws_access_key"),
    # anchoring (6b): a credential glued to a preceding word character is
    # no longer hidden from detection by the leading boundary.
    (f"prefix{_FAKE_AWS_KEY}", "aws_access_key"),
    # trailing-glue anchoring: the mirror image of 6b on the trailing edge.
    (f"{_FAKE_AWS_KEY}suffix", "aws_access_key"),
    # separators (6d): a PESEL split by a single hyphen is still caught.
    ("440514-01359", "pesel"),
    ("440514 01359", "pesel"),
    # PESEL false positives (6c): a plausible 11-digit phone number whose
    # month field (digits[2:4] % 20) falls outside 1-12 is not flagged.
    ("48771378733", None),
    # a 2000s-era PESEL (month field 25 -> 2005-05-14): every other PESEL
    # case here is a 1900s one, so this guards against a future
    # "simplification" of the `% 20` century check to a plain 1-12 range.
    ("05251401356", "pesel"),
    # regression: dropping the leading anchor on the openai pattern (6b)
    # must not make ordinary hyphenated technical prose match "sk-" plus a
    # long alphanumeric run split by hyphens.
    ("please review risk-assessment-and-mitigation-plan.md", None),
    ("the task-scheduler-service-config.yaml is failing", None),
    ("helpdesk-ticket-escalation-matrix-2026", None),
    ("asterisk-pbx-configuration-notes-updated", None),
    # a realistic sk-proj- style key must still be caught.
    (f"key: {_FAKE_OPENAI_PROJECT_KEY}", "openai_api_key"),
]


@pytest.mark.parametrize("text,expected_rule", CASES)
def test_scan_text(text, expected_rule):
    match = scan_text(text)
    if expected_rule is None:
        assert match is None
    else:
        assert match is not None
        assert match.rule == expected_rule
