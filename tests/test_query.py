import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_query_endpoint_success(async_client: AsyncClient):
    payload = {"query": "What is enterprise hybrid search?"}
    response = await async_client.post("/api/v1/rag/query", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "data:" in response.text


@pytest.mark.asyncio
async def test_query_endpoint_fails_on_short_query(async_client: AsyncClient):
    payload = {"query": "Hi"}
    response = await async_client.post("/api/v1/rag/query", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
