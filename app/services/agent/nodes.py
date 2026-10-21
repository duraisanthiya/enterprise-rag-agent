from app.core.qdrant import get_qdrant_client
from app.services.agent.state import AgentState
from app.services.retrieval.reranker import rerank_documents
from app.services.retrieval.search import hybrid_search

# Calibrated threshold for BAAI/bge-reranker-base logits
RELEVANCE_THRESHOLD = -4.0

async def retrieve_node(state: AgentState) -> dict:
    """Node 1: Executes hybrid retrieval and cross-encoder reranking

    using the query currently stored in the state.
    """
    query = state["current_query"]
    client = get_qdrant_client()

    # Stage 1: Hybrid Search
    candidates = await hybrid_search(
        client=client,
        query_text=query,
        top_k=6,
    )

    # Stage 2: Cross-Encoder Reranking
    top_docs = rerank_documents(
        query=query,
        candidates=candidates,
        top_n=3,
    )

    return {"documents": top_docs}

async def grade_documents_node(state: AgentState) -> dict:
    """Node 2: Evaluates whether the retrieved documents contain sufficient,

    relevant information to answer the user query.
    """
    docs = state.get("documents", [])

    if not docs:
        return {"context_quality": "poor"}

    top_score = docs[0].score
    if top_score >= RELEVANCE_THRESHOLD:
        quality = "relevant"
    else:
        quality = "poor"

    return {"context_quality": quality}

async def rewrite_query_node(state: AgentState) -> dict:
    """Node 3: Self-correction.

    Reformulates the query to broaden recall and increments the retry counter.
    """
    current_query = state["current_query"]
    retries = state.get("retry_count", 0) + 1

    rewritten_query = (
        f"{current_query} technical overview specifications guide"
    )

    print(
        f"🔄 Self-correction triggered (Attempt {retries}/{state['max_retries']}):"
    )
    print(f"   Original:  '{current_query}'")
    print(f"   Rewritten: '{rewritten_query}'")

    return {
        "current_query": rewritten_query,
        "retry_count": retries,
    }

async def generate_node(state: AgentState) -> dict:
    """Node 4: Synthesizes the final answer using retrieved context,

    or provides a safe fallback if retrieval confidence failed.
    """
    quality = state.get("context_quality", "poor")
    docs = state.get("documents", [])
    original_query = state["original_query"]

    # If context is poor, fail safely regardless of whether nearest neighbors exist!
    if quality == "poor":
        fallback_msg = (
            f"I searched the enterprise knowledge base for '{original_query}', "
            "but could not find verified documentation to answer with confidence."
        )
        return {"generation": fallback_msg}

    # Grounded Synthesis Path
    context_text = "\n\n".join(
        [f"[Doc {idx+1}]: {d.text}" for idx, d in enumerate(docs)]
    )

    answer = (
        f"Based on verified enterprise documentation:\n{context_text}\n\n"
        f"Summary: The query '{original_query}' has been resolved with {len(docs)} cited context chunks."
    )

    return {"generation": answer}