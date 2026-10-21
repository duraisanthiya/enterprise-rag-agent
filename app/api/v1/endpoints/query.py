from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from app.schemas.rag import QueryRequest
from app.services.agent.graph import agent_app
from app.services.agent.state import AgentState
from app.services.streaming import stream_agent_execution

router = APIRouter()

@router.post(
    "/query",
    status_code=status.HTTP_200_OK,
    summary="Query the RAG Agent",
)
async def query_rag(request: QueryRequest) -> StreamingResponse:
    """Executes the LangGraph Corrective RAG Agent workflow

    (Retrieve -> Grade -> Self-Correct -> Synthesize) and streams live SSE
    events.
    """
    # 1. Initialize Graph State
    initial_state: AgentState = {
        "original_query": request.query,
        "current_query": request.query,
        "documents": [],
        "context_quality": "pending",
        "retry_count": 0,
        "max_retries": 2,
        "generation": None,
    }

    # 2. Execute the compiled LangGraph Agent state machine
    final_state = await agent_app.ainvoke(initial_state)

    # 3. Stream agent execution steps and tokens
    return StreamingResponse(
        stream_agent_execution(final_state),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )