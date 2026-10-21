import pytest
from httpx import AsyncClient
from app.core.qdrant import close_qdrant, init_qdrant
from app.services.retrieval.collection import setup_hybrid_collection

@pytest.mark.asyncio
async def test_query_endpoint_success(async_client: AsyncClient):
    """Test sending a valid query returns 200 and text/event-stream content."""
    client = await init_qdrant()
    await setup_hybrid_collection(client)

    payload = {"query": "What is our cloud migration timeline?"}
    response = await async_client.post("/api/v1/rag/query", json=payload)

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "data:" in response.text

    await close_qdrant()

@pytest.mark.asyncio
async def test_query_endpoint_fails_on_short_query(async_client: AsyncClient):
    """Test that Pydantic rejects a query that is too short (min_length=3)."""
    payload = {"query": "Hi"}
    response = await async_client.post("/api/v1/rag/query", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data