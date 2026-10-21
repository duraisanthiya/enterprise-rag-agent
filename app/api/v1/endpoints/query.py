from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from app.core.qdrant import get_qdrant_client
from app.schemas.rag import QueryRequest
from app.services.retrieval.reranker import rerank_documents
from app.services.retrieval.search import hybrid_search
from app.services.streaming import stream_rag_response

router = APIRouter()

@router.post(
    "/query",
    status_code=status.HTTP_200_OK,
    summary="Query the RAG Agent",
)
async def query_rag(request: QueryRequest) -> StreamingResponse:
    """Executes Two-Stage Hybrid Retrieval (Dense HNSW + Sparse BM25 + Reranking)

    and streams results via Server-Sent Events.
    """
    client = get_qdrant_client()

    # Stage 1: Hybrid Search with RRF (retrieve candidates)
    candidates = await hybrid_search(
        client=client,
        query_text=request.query,
        top_k=request.top_k * 2,
        filter_conditions=request.metadata_filters,
    )

    # Stage 2: Cross-Encoder Reranking (refine to top_k)
    final_docs = rerank_documents(
        query=request.query,
        candidates=candidates,
        top_n=request.top_k,
    )

    # Return SSE stream
    return StreamingResponse(
        stream_rag_response(query=request.query, retrieved_docs=final_docs),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )