import asyncio
import json
from typing import AsyncGenerator


async def mock_stream_tokens(query: str) -> AsyncGenerator[str, None]:
    """Simulates an LLM token-by-token streaming generator using SSE format."""
    mock_response = (
        f"Processing query: '{query}'. "
        "Enterprise RAG architecture initialized. "
        "Hybrid retrieval with dense embeddings and BM25 search will run here."
    )

    words = mock_response.split(" ")
    for word in words:
        await asyncio.sleep(0.03)
        payload = {"token": word + " "}
        yield f"data: {json.dumps(payload)}\n\n"

    yield "data: [DONE]\n\n"
