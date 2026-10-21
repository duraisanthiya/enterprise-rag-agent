import pytest
from app.services.agent.state import AgentState

def test_agent_state_initialization():
    """Verify AgentState contract structure and default values."""
    initial_state: AgentState = {
        "original_query": "What is the AKS migration timeline?",
        "current_query": "What is the AKS migration timeline?",
        "documents": [],
        "context_quality": "pending",
        "retry_count": 0,
        "max_retries": 2,
        "generation": None,
    }

    assert initial_state["original_query"] == initial_state["current_query"]
    assert initial_state["retry_count"] == 0
    assert initial_state["max_retries"] == 2
    assert initial_state["generation"] is None