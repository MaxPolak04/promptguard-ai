from app.rules import scan_text


def test_detects_aws_access_key():
    match = scan_text("here is AKIAIOSFODNN7EXAMPLE ok")  # pragma: allowlist secret
    assert match is not None
    assert match.rule == "aws_access_key"


def test_detects_openai_api_key():
    text = "key: sk-abcdefghijklmnopqrstuvwxyz123456"  # pragma: allowlist secret
    match = scan_text(text)
    assert match is not None
    assert match.rule == "openai_api_key"


def test_detects_private_key_block():
    match = scan_text("-----BEGIN RSA PRIVATE KEY-----")  # pragma: allowlist secret
    assert match is not None
    assert match.rule == "private_key_block"


def test_detects_valid_pesel():
    match = scan_text("my id is 44051401359")
    assert match is not None
    assert match.rule == "pesel"


def test_ignores_11_digits_with_bad_checksum():
    assert scan_text("number 44051401358 here") is None


def test_clean_text_returns_none():
    assert scan_text("What is the capital of France?") is None
