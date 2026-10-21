from typing import Any
from pydantic import BaseModel
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from app.core.config import settings
from app.services.retrieval.collection import (
    DENSE_VECTOR_NAME,
    SPARSE_VECTOR_NAME,
)
from app.services.retrieval.indexer import dense_model, sparse_model

class SearchResult(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: dict[str, Any]

async def hybrid_search(
    client: AsyncQdrantClient,
    query_text: str,
    top_k: int = 5,
    filter_conditions: dict[str, Any] | None = None,
) -> list[SearchResult]:
    """Executes a two-stage hybrid search in Qdrant:

    1. Dense semantic search (HNSW)
    2. Sparse keyword search (BM25)
    3. Fuses both candidate lists using native Reciprocal Rank Fusion (RRF)
    """
    # 1. Embed query into Dense vector (384-dim)
    dense_query = list(dense_model.embed([query_text]))[0].tolist()

    # 2. Embed query into Sparse BM25 vector
    sparse_query_obj = list(sparse_model.embed([query_text]))[0]
    sparse_query = models.SparseVector(
        indices=sparse_query_obj.indices.tolist(),
        values=sparse_query_obj.values.tolist(),
    )

    # 3. Build metadata filters if provided (e.g. department == 'Security')
    qdrant_filter = None
    if filter_conditions:
        must_conditions = [
            models.FieldCondition(
                key=key, match=models.MatchValue(value=val)
            )
            for key, val in filter_conditions.items()
        ]
        qdrant_filter = models.Filter(must=must_conditions)

    # 4. Native Qdrant Hybrid Query with RRF Fusion
    response = await client.query_points(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        prefetch=[
            # Candidate set 1: Dense Semantic Search
            models.Prefetch(
                query=dense_query,
                using=DENSE_VECTOR_NAME,
                limit=top_k * 2,
                filter=qdrant_filter,
            ),
            # Candidate set 2: Sparse BM25 Keyword Search
            models.Prefetch(
                query=sparse_query,
                using=SPARSE_VECTOR_NAME,
                limit=top_k * 2,
                filter=qdrant_filter,
            ),
        ],
        # Fuse candidate sets using Reciprocal Rank Fusion
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=top_k,
    )

    # 5. Unpack points into clean Pydantic SearchResult objects
    results: list[SearchResult] = []
    for point in response.points:
        payload = point.payload or {}
        text = payload.get("text", "")
        metadata = {k: v for k, v in payload.items() if k != "text"}

        results.append(
            SearchResult(
                chunk_id=str(point.id),
                text=text,
                score=point.score,
                metadata=metadata,
            )
        )

    return results