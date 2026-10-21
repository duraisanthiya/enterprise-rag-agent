import asyncio
import json
from typing import AsyncGenerator
from app.services.agent.state import AgentState

async def stream_agent_execution(
    state: AgentState,
) -> AsyncGenerator[str, None]:
    """Streams the LangGraph Agent's self-correction steps, citations,

    and final synthesized response via Server-Sent Events (SSE).
    """
    retries = state.get("retry_count", 0)
    quality = state.get("context_quality", "unknown")
    current_q = state.get("current_query", "")

    # 1. Stream self-correction event if retries occurred
    if retries > 0:
        correction_msg = (
            f"Self-correction triggered ({retries} rewrites). "
            f"Query reformulated to: '{current_q}'"
        )
        correction_payload = json.dumps({"agent_step": correction_msg})
        yield f"data: {correction_payload}\n\n"
        await asyncio.sleep(0.04)

    # 2. Stream context quality diagnostic event
    quality_msg = f"Context evaluation: {quality.upper()} ({len(state.get('documents', []))} chunks evaluated)"
    quality_payload = json.dumps({"agent_step": quality_msg})
    yield f"data: {quality_payload}\n\n"
    await asyncio.sleep(0.04)

    # 3. Stream source citations payload
    citations = [
        {
            "chunk_id": doc.chunk_id,
            "text": doc.text,
            "score": round(doc.score, 4),
            "metadata": doc.metadata,
        }
        for doc in state.get("documents", [])
    ]
    citations_payload = json.dumps({"citations": citations})
    yield f"data: {citations_payload}\n\n"
    await asyncio.sleep(0.04)

    # 4. Stream generated response token-by-token
    generation = state.get(
        "generation", "No generation produced by the agent."
    )
    for word in generation.split(" "):
        await asyncio.sleep(0.02)
        token_payload = json.dumps({"token": word + " "})
        yield f"data: {token_payload}\n\n"

    # 5. Stream completion signal
    yield "data: [DONE]\n\n"