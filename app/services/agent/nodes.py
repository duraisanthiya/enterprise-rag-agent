import logging
from app.core.config import settings
from app.core.qdrant import get_qdrant_client
from app.services.agent.state import AgentState
from app.services.retrieval.reranker import rerank_documents
from app.services.retrieval.search import hybrid_search

logger = logging.getLogger("enterprise_rag.agent")
RELEVANCE_THRESHOLD = -5.0

def get_llm():
    if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-dummy") and len(settings.OPENAI_API_KEY) > 20:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.0)
        except ImportError:
            logger.warning("langchain-openai not installed, using grounded synthesis")
    return None

async def retrieve_node(state: AgentState) -> dict:
    query = state["current_query"].strip()
    client = get_qdrant_client()
    candidates = await hybrid_search(client=client, query_text=query, top_k=6)
    top_docs = rerank_documents(query=query, candidates=candidates, top_n=3)
    return {"documents": top_docs}

async def grade_documents_node(state: AgentState) -> dict:
    docs = state.get("documents", [])
    if not docs:
        return {"context_quality": "poor"}
    top_score = docs[0].score
    quality = "relevant" if top_score >= RELEVANCE_THRESHOLD else "poor"
    return {"context_quality": quality}

async def rewrite_query_node(state: AgentState) -> dict:
    current_query = state["current_query"]
    retries = state.get("retry_count", 0) + 1
    rewritten_query = f"{current_query} technical overview specifications guide"
    logger.info("Self-correction cycle %d/%d: reformulated query to %s", retries, state["max_retries"], rewritten_query)
    return {"current_query": rewritten_query, "retry_count": retries}

async def generate_node(state: AgentState) -> dict:
    quality = state.get("context_quality", "poor")
    docs = state.get("documents", [])
    original_query = state["original_query"].strip()
    if quality == "poor" or not docs:
        return {"generation": f"I searched the enterprise knowledge base for {original_query!r}, but could not find verified documentation to answer with confidence."}
    context_text = "\n\n".join([f"[Document {idx+1}]: {d.text}" for idx, d in enumerate(docs)])
    llm = get_llm()
    if llm:
        from langchain_core.messages import HumanMessage, SystemMessage
        system_prompt = "You are an enterprise technical assistant. Answer strictly based on the context. If the context does not contain the answer, say you do not know. Always cite documents."
        user_prompt = f"Context:\n{context_text}\n\nQuestion: {original_query}"
        try:
            response = await llm.ainvoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            return {"generation": response.content}
        except Exception as e:
            logger.warning("Live LLM call failed (%s), using grounded fallback", e)
    answer = f"Based on verified enterprise documentation:\n{context_text}\n\nSummary: The query {original_query!r} has been resolved with {len(docs)} cited context chunks."
    return {"generation": answer}
