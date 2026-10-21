import asyncio
import json
from typing import AsyncGenerator
from app.services.retrieval.search import SearchResult

async def stream_rag_response(
    query: str, retrieved_docs: list[SearchResult]
) -> AsyncGenerator[str, None]:
    """Streams RAG status, retrieved citations, and synthesized tokens via SSE."""
    # 1. Emit retrieval status
    yield f"data: {json.dumps({'status': f'Retrieved {len(retrieved_docs)} relevant context chunks.'})}\n\n"
    await asyncio.sleep(0.05)

    # 2. Emit source citations payload
    citations = [
        {
            "chunk_id": doc.chunk_id,
            "text": doc.text,
            "score": round(doc.score, 4),
            "metadata": doc.metadata,
        }
        for doc in retrieved_docs
    ]
    yield f"data: {json.dumps({'citations': citations})}\n\n"
    await asyncio.sleep(0.05)

    # 3. Simulate synthesized answer stream (in Week 3, this connects to LangGraph Agent)
    context_summary = " ".join([d.text for d in retrieved_docs])
    response_text = (
        f"Based on the enterprise knowledge base: {context_summary}"
    )

    for word in response_text.split(" "):
        await asyncio.sleep(0.02)
        yield f"data: {json.dumps({'token': word + ' '})}\n\n"

    # 4. Stream completion signal
    yield "data: [DONE]\n\n"