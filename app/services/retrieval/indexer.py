import uuid
from typing import Any
from fastembed import SparseTextEmbedding, TextEmbedding
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from app.core.config import settings
from app.services.retrieval.collection import (
    DENSE_VECTOR_NAME,
    SPARSE_VECTOR_NAME,
)

# Initialize FastEmbed models (they run locally on CPU via ONNX Runtime)
dense_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")


class DocumentChunk:

    def __init__(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        chunk_id: str | None = None,
    ):
        self.chunk_id = chunk_id or str(uuid.uuid4())
        self.text = text
        self.metadata = metadata or {}


async def index_documents(
    client: AsyncQdrantClient, chunks: list[DocumentChunk]
) -> int:
    """Computes both Dense (HNSW) and Sparse (BM25) embeddings for documents

    and upserts them into Qdrant.
    """
    if not chunks:
        return 0

    texts = [chunk.text for chunk in chunks]

    # 1. Compute Dense Vectors (384-dimensional semantic embeddings)
    dense_embeddings = list(dense_model.embed(texts))

    # 2. Compute Sparse Vectors (BM25 keyword tokens and weights)
    sparse_embeddings = list(sparse_model.embed(texts))

    # 3. Build Qdrant Point objects
    points: list[models.PointStruct] = []
    for idx, chunk in enumerate(chunks):
        dense_vec = dense_embeddings[idx].tolist()
        sparse_vec = sparse_embeddings[idx]

        point = models.PointStruct(
            id=chunk.chunk_id,
            vector={
                DENSE_VECTOR_NAME: dense_vec,
                SPARSE_VECTOR_NAME: models.SparseVector(
                    indices=sparse_vec.indices.tolist(),
                    values=sparse_vec.values.tolist(),
                ),
            },
            payload={
                "text": chunk.text,
                **chunk.metadata,
            },
        )
        points.append(point)

    # 4. Upsert into Qdrant
    await client.upsert(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points=points,
        wait=True,  # Blocks until vectors are fully committed to the index
    )

    return len(points)