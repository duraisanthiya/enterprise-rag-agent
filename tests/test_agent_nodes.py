import pytest
from app.core.qdrant import close_qdrant, init_qdrant
from app.services.agent.nodes import grade_documents_node, retrieve_node
from app.services.agent.state import AgentState
from app.services.retrieval.collection import setup_hybrid_collection
from app.services.retrieval.indexer import DocumentChunk, index_documents
from app.services.retrieval.search import SearchResult

@pytest.mark.asyncio
async def test_retrieve_and_grade_nodes():
    """Verify retrieve_node fetches documents and grade_documents_node flags quality."""
    # 1. Setup DB and test data
    client = await init_qdrant()
    await setup_hybrid_collection(client)
    await index_documents(
        client,
        [
            DocumentChunk(
                text="The AKS cloud cluster migration is scheduled for Q4 2026."
            )
        ],
    )

    state: AgentState = {
        "original_query": "When is the AKS cloud migration?",
        "current_query": "When is the AKS cloud migration?",
        "documents": [],
        "context_quality": "pending",
        "retry_count": 0,
        "max_retries": 2,
        "generation": None,
    }

    # 2. Execute retrieve_node
    retrieval_update = await retrieve_node(state)
    state["documents"] = retrieval_update["documents"]
    assert len(state["documents"]) > 0
    assert "AKS" in state["documents"][0].text

    # 3. Execute grade_documents_node on good context
    grade_update = await grade_documents_node(state)
    assert grade_update["context_quality"] == "relevant"

    # 4. Verify grade_documents_node marks empty context as 'poor'
    empty_state: AgentState = {**state, "documents": []}
    poor_grade_update = await grade_documents_node(empty_state)
    assert poor_grade_update["context_quality"] == "poor"

    await close_qdrant()