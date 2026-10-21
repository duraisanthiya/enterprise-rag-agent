import pytest
from app.core.config import settings
from app.core.qdrant import close_qdrant, init_qdrant
from app.services.retrieval.collection import (
    DENSE_VECTOR_NAME,
    SPARSE_VECTOR_NAME,
    setup_hybrid_collection,
)


@pytest.mark.asyncio
async def test_hybrid_collection_initialization():
    """Verify that the collection is created with both Dense and Sparse vector configurations."""
    # 1. Connect
    client = await init_qdrant()

    # 2. Setup collection
    await setup_hybrid_collection(client)

    # 3. Inspect collection info from Qdrant
    info = await client.get_collection(
        collection_name=settings.QDRANT_COLLECTION_NAME
    )

    # 4. Assert Dense & Sparse vectors exist
    assert DENSE_VECTOR_NAME in info.config.params.vectors
    assert info.config.params.vectors[DENSE_VECTOR_NAME].size == 384
    assert SPARSE_VECTOR_NAME in info.config.params.sparse_vectors

    # 5. Clean up connection
    await close_qdrant()