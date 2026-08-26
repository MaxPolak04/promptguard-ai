import httpx
import pytest

from app.llm import LLMClient, LLMError


def _client(handler) -> LLMClient:
    return LLMClient(
        api_base="https://llm.test/v1",
        api_key="test-key",
        model="test-model",
        transport=httpx.MockTransport(handler),
    )


async def test_complete_returns_message_text():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-key"
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "hi there"}}]}
        )

    client = _client(handler)
    assert await client.complete("hello") == "hi there"
    await client.aclose()


async def test_transport_error_raises_llm_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    client = _client(handler)
    with pytest.raises(LLMError):
        await client.complete("hello")
    await client.aclose()


async def test_http_error_raises_llm_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    client = _client(handler)
    with pytest.raises(LLMError):
        await client.complete("hello")
    await client.aclose()


async def test_malformed_payload_raises_llm_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": True})

    client = _client(handler)
    with pytest.raises(LLMError):
        await client.complete("hello")
    await client.aclose()


async def test_non_json_body_raises_llm_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"<html>not json</html>")

    client = _client(handler)
    with pytest.raises(LLMError):
        await client.complete("hello")
    await client.aclose()


async def test_null_content_raises_llm_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": None}}]})

    client = _client(handler)
    with pytest.raises(LLMError):
        await client.complete("hello")
    await client.aclose()
