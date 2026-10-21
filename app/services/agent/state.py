from typing import Annotated, TypedDict
from app.services.retrieval.search import SearchResult

def replace_list(existing: list, new_val: list) -> list:
    """Reducer function: Replaces the existing list with the updated one."""
    return new_val

class AgentState(TypedDict):
    """The central state of our Corrective RAG (CRAG) Agent Graph.

    Passed between every node in the workflow.
    """

    # The original question submitted by the user
    original_query: str

    # The reformulated query (if self-correction was triggered)
    current_query: str

    # Retrieved candidate documents from Qdrant
    documents: Annotated[list[SearchResult], replace_list]

    # Binary quality grade: 'relevant' or 'poor'
    context_quality: str

    # Self-correction loop counter (prevents infinite loops!)
    retry_count: int

    # Maximum allowed query reformulations before fallback
    max_retries: int

    # Final generated answer text
    generation: str | None