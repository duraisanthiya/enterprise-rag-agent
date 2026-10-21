import pytest
from app.core.qdrant import close_qdrant, init_qdrant
from app.services.retrieval.collection import setup_hybrid_collection
from app.services.retrieval.indexer import DocumentChunk, index_documents
from app.services.retrieval.search import hybrid_search

@pytest.mark.asyncio
async def test_hybrid_search_retrieves_semantic_and_keyword_matches():
    """Verify hybrid search works across conceptual queries and exact serial codes."""
    client = await init_qdrant()
    await setup_hybrid_collection(client)

    # Ingest test enterprise data
    test_docs = [
        DocumentChunk(
            text="Azure Kubernetes Service (AKS) cluster migration is scheduled for Q4.",
            metadata={"department": "DevOps"},
        ),
        DocumentChunk(
            text="Error code 0x80070005 indicates unauthorized access permissions in Edge.",
            metadata={"department": "Security"},
        ),
    ]
    await index_documents(client, test_docs)

    # 1. Semantic Query: Conceptual match without using the word 'Kubernetes'
    semantic_results = await hybrid_search(
        client, query_text="When are we moving cloud infrastructure?", top_k=1
    )
    assert len(semantic_results) > 0
    assert "Kubernetes" in semantic_results[0].text

    # 2. Exact Keyword Query: BM25 exact match
    keyword_results = await hybrid_search(
        client, query_text="0x80070005", top_k=1
    )
    assert len(keyword_results) > 0
    assert "unauthorized access" in keyword_results[0].text

    await close_qdrant()