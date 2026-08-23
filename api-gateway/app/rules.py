import re
from dataclasses import dataclass

# No leading anchor: an attacker can defeat a `\b`- or alnum-lookbehind-based
# anchor simply by gluing one more letter or digit onto the front of the key,
# and evading detection is this product's threat model. A trailing `\b` is
# kept so the match doesn't run on into unrelated following characters.
_PATTERNS: dict[str, re.Pattern[str]] = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}\b", re.IGNORECASE),
    "openai_api_key": re.compile(r"sk-[A-Za-z0-9_-]{20,}\b", re.IGNORECASE),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}

# Tolerates a single '-' or ' ' separator (e.g. "440514-01359"); the exact
# digit count is enforced after stripping, in _is_valid_pesel's caller.
_PESEL_CANDIDATE = re.compile(r"\b\d{11}\b|\b\d{1,10}[-\s]\d{1,10}\b")
_PESEL_WEIGHTS = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)


@dataclass(frozen=True)
class RuleMatch:
    """A sensitive-data rule that matched the scanned text."""

    rule: str


def _is_valid_pesel(digits: str) -> bool:
    """Check the checksum and the YYMMDD date sanity of an 11-digit PESEL.

    The month field encodes the century by adding 0/20/40/60/80, hence the
    `% 20`. The checksum alone admits about 1 in 10 arbitrary 11-digit
    strings; requiring a plausible month and day rejects most of the
    phone numbers, order ids, and timestamps that would otherwise pass it
    by chance.
    """
    month = int(digits[2:4]) % 20
    day = int(digits[4:6])
    if not (1 <= month <= 12) or not (1 <= day <= 31):
        return False
    checksum = sum(int(d) * w for d, w in zip(digits[:10], _PESEL_WEIGHTS))
    return (10 - checksum % 10) % 10 == int(digits[10])


def scan_text(text: str) -> RuleMatch | None:
    """Return the first sensitive-data rule matching the text, if any."""
    for rule, pattern in _PATTERNS.items():
        if pattern.search(text):
            return RuleMatch(rule=rule)
    for candidate in _PESEL_CANDIDATE.findall(text):
        digits = candidate.replace("-", "").replace(" ", "")
        if len(digits) == 11 and _is_valid_pesel(digits):
            return RuleMatch(rule="pesel")
    return None
