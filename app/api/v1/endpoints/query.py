from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from app.schemas.rag import QueryRequest
from app.services.streaming import mock_stream_tokens

router = APIRouter()


@router.post(
    "/query",
    status_code=status.HTTP_200_OK,
    summary="Query the RAG Agent",
)
async def query_rag(request: QueryRequest) -> StreamingResponse:
    return StreamingResponse(
        mock_stream_tokens(request.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
