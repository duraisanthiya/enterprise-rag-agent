import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_middleware_attaches_tracing_headers(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert "x-process-time" in response.headers
    assert response.headers["x-process-time"].endswith("s")
