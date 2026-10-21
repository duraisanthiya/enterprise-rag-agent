import pytest
from app.core.qdrant import close_qdrant, init_qdrant
from app.services.agent.graph import agent_app
from app.services.agent.state import AgentState
from app.services.retrieval.collection import setup_hybrid_collection
from app.services.retrieval.indexer import DocumentChunk, index_documents

@pytest.mark.asyncio
async def test_agent_graph_happy_path():
    """Test graph execution when relevant documents exist."""
    client = await init_qdrant()
    await setup_hybrid_collection(client)
    await index_documents(
        client,
        [
            DocumentChunk(
                text="Microsoft Edge data science telemetry pipeline is operational."
            )
        ],
    )

    initial_state: AgentState = {
        "original_query": "What is the status of the Edge telemetry pipeline?",
        "current_query": "What is the status of the Edge telemetry pipeline?",
        "documents": [],
        "context_quality": "pending",
        "retry_count": 0,
        "max_retries": 2,
        "generation": None,
    }

    # Execute the compiled graph
    final_state = await agent_app.ainvoke(initial_state)

    assert final_state["generation"] is not None
    assert "telemetry pipeline" in final_state["generation"]
    assert final_state["context_quality"] == "relevant"
    assert final_state["retry_count"] == 0

    await close_qdrant()

@pytest.mark.asyncio
async def test_agent_graph_self_correction_fallback():
    """Test graph triggers rewrite loop and safe fallback when no docs match."""
    client = await init_qdrant()
    await setup_hybrid_collection(client)

    # Query something that definitely does not exist in our vector database
    initial_state: AgentState = {
        "original_query": "CompletelyUnknownTopicWithZeroMatchesXYZ123",
        "current_query": "CompletelyUnknownTopicWithZeroMatchesXYZ123",
        "documents": [],
        "context_quality": "pending",
        "retry_count": 0,
        "max_retries": 2,
        "generation": None,
    }

    # Execute graph
    final_state = await agent_app.ainvoke(initial_state)

    # Assert that self-correction tried up to max_retries
    assert final_state["retry_count"] == 2
    assert final_state["generation"] is not None
    assert (
        "could not find verified documentation" in final_state["generation"]
    )

    await close_qdrant()