from langgraph.graph import END, START, StateGraph
from app.services.agent.nodes import (
    generate_node,
    grade_documents_node,
    retrieve_node,
    rewrite_query_node,
)
from app.services.agent.state import AgentState

def decide_to_generate(state: AgentState) -> str:
    """Conditional Edge: Decides whether to proceed to generation

    or loop back to rewrite the query.
    """
    quality = state.get("context_quality", "poor")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    # 1. If context is high quality, generate answer immediately
    if quality == "relevant":
        return "generate"

    # 2. If context is poor but we haven't hit the loop limit, self-correct!
    if retry_count < max_retries:
        return "rewrite_query"

    # 3. If retries are exhausted, proceed to generate safe fallback
    return "generate"

def create_agent_graph():
    """Compiles the stateful LangGraph Corrective RAG workflow."""
    workflow = StateGraph(AgentState)

    # 1. Register all nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade_documents", grade_documents_node)
    workflow.add_node("rewrite_query", rewrite_query_node)
    workflow.add_node("generate", generate_node)

    # 2. Define deterministic transitions
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "grade_documents")

    # 3. Define conditional branching (Self-Correction loop vs Generation)
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "generate": "generate",
            "rewrite_query": "rewrite_query",
        },
    )

    # 4. Loop back: after rewriting query, search again!
    workflow.add_edge("rewrite_query", "retrieve")

    # 5. Terminate
    workflow.add_edge("generate", END)

    # Compile the state machine
    return workflow.compile()

# Compiled singleton graph
agent_app = create_agent_graph()