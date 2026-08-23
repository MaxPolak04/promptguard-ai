import re
from dataclasses import dataclass

_PATTERNS: dict[str, re.Pattern[str]] = {
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "openai_api_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}

_PESEL_CANDIDATE = re.compile(r"\b\d{11}\b")
_PESEL_WEIGHTS = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)


@dataclass(frozen=True)
class RuleMatch:
    """A sensitive-data rule that matched the scanned text."""

    rule: str


def _is_valid_pesel(digits: str) -> bool:
    checksum = sum(int(d) * w for d, w in zip(digits[:10], _PESEL_WEIGHTS))
    return (10 - checksum % 10) % 10 == int(digits[10])


def scan_text(text: str) -> RuleMatch | None:
    """Return the first sensitive-data rule matching the text, if any."""
    for rule, pattern in _PATTERNS.items():
        if pattern.search(text):
            return RuleMatch(rule=rule)
    for candidate in _PESEL_CANDIDATE.findall(text):
        if _is_valid_pesel(candidate):
            return RuleMatch(rule="pesel")
    return None
