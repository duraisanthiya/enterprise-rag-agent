from unittest.mock import patch
import pytest
from httpx import AsyncClient
from app.core.exceptions import VectorStoreUnavailableError

@pytest.mark.asyncio
async def test_vector_store_error_returns_clean_503(async_client: AsyncClient):
    """Simulate a failure during agent execution and verify the global handler intercepts it cleanly."""
    with patch(
        "app.api.v1.endpoints.query.agent_app.ainvoke",
        side_effect=VectorStoreUnavailableError(
            "Connection to Qdrant timed out."
        ),
    ):
        response = await async_client.post(
            "/api/v1/rag/query", json={"query": "Test database failure"}
        )

        assert response.status_code == 503
        data = response.json()
        assert data["error_code"] == "VECTOR_STORE_UNAVAILABLE"
        assert data["message"] == "Connection to Qdrant timed out."
        assert "timestamp" in data