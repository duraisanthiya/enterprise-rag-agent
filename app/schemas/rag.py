from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="The user input query to the RAG system",
        examples=["What is our cloud migration timeline?"],
    )
    conversation_id: UUID = Field(
        default_factory=uuid4,
        description="Session identifier for multi-turn history",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of chunks to retrieve (1 <= top_k <= 20)",
    )
    metadata_filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value filters for scoped retrieval",
    )
    stream: bool = Field(
        default=True,
        description="Whether to stream response tokens via SSE",
    )
