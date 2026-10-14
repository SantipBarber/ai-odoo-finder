"""Tests for the MCP server: request building, version validation and /health.

Run from mcp-server/:
    uv run --with pytest pytest tests
"""

import httpx
import pytest
from starlette.testclient import TestClient

from ai_odoofinder_mcp import server

SAMPLE_RESULT = {
    "results": [
        {
            "technical_name": "sale_order_type",
            "name": "Sale Order Type",
            "score": 92,
            "repo_name": "sale-workflow",
            "version": "17.0",
        }
    ]
}


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def captured(monkeypatch):
    """Replace the backend with a mock transport and record the requests."""
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=SAMPLE_RESULT)

    async def fake_client() -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url="http://backend.test", transport=httpx.MockTransport(handler)
        )

    monkeypatch.setattr(server, "get_http_client", fake_client)
    return requests


search = server.search_odoo_modules.fn


@pytest.mark.anyio
async def test_dependencies_are_sent_as_repeated_params(captured):
    await search(query="sales", version="17.0", dependencies=["sale", "stock"])

    params = captured[0].url.params
    assert params.get_list("dependencies") == ["sale", "stock"]


@pytest.mark.anyio
async def test_no_dependencies_param_when_not_given(captured):
    await search(query="sales", version="17.0")

    assert "dependencies" not in captured[0].url.params


@pytest.mark.anyio
@pytest.mark.parametrize("version", ["10.0", "11.0", "20.0"])
async def test_unsupported_versions_are_rejected_without_calling_backend(captured, version):
    result = await search(query="sales", version=version)

    assert "Invalid version" in result
    assert captured == []


@pytest.mark.anyio
@pytest.mark.parametrize("version", server.SUPPORTED_VERSIONS)
async def test_supported_versions_reach_backend(captured, version):
    result = await search(query="sales", version=version)

    assert captured[0].url.params["version"] == version
    assert "sale_order_type" in result


@pytest.mark.anyio
async def test_limit_is_clamped(captured):
    await search(query="sales", version="17.0", limit=99)

    assert captured[0].url.params["limit"] == "20"


def test_health_route():
    with TestClient(server.mcp.http_app(path="/")) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
