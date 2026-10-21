from qdrant_client import AsyncQdrantClient
from app.core.config import settings

# Global client singleton reference
_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    """Dependency provider: Injects the active Qdrant client into services."""
    if _client is None:
        raise RuntimeError("Qdrant client is not initialized. Check lifespan startup.")
    return _client


async def init_qdrant() -> AsyncQdrantClient:
    """Initializes the connection pool on application startup."""
    global _client
    _client = AsyncQdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        check_compatibility=False,  # Silences the version check warning
    )
    return _client


async def close_qdrant() -> None:
    """Closes all open network sockets on application shutdown."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None