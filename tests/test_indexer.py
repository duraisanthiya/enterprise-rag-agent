import pytest
from app.core.config import settings
from app.core.qdrant import close_qdrant, init_qdrant
from app.services.retrieval.collection import setup_hybrid_collection
from app.services.retrieval.indexer import DocumentChunk, index_documents

@pytest.mark.asyncio
async def test_indexing_documents_into_qdrant():
    """Verify that document chunks are embedded and successfully stored in Qdrant."""
    client = await init_qdrant()
    await setup_hybrid_collection(client)

    sample_chunks = [
        DocumentChunk(
            text="Azure Kubernetes Service (AKS) cluster migration is scheduled for Q4.",
            metadata={"department": "DevOps", "doc_type": "policy"},
        ),
        DocumentChunk(
            text="Error code 0x80070005 indicates unauthorized access permissions in Edge.",
            metadata={"department": "Security", "doc_type": "troubleshooting"},
        ),
    ]

    # Index the sample documents
    count = await index_documents(client, sample_chunks)
    assert count == 2

    # Verify points exist in Qdrant
    info = await client.get_collection(settings.QDRANT_COLLECTION_NAME)
    assert info.points_count >= 2

    await close_qdrant()