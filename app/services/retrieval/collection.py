from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from app.core.config import settings

# Names of our dual vector spaces
DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"

# Dimension for fastembed 'BAAI/bge-small-en-v1.5' model
DENSE_VECTOR_SIZE = 384


async def setup_hybrid_collection(client: AsyncQdrantClient) -> None:
    """Ensures the Qdrant hybrid collection exists with Dense (HNSW)

    and Sparse (BM25) vector configurations.
    """
    collection_name = settings.QDRANT_COLLECTION_NAME

    # 1. Check if collection already exists
    exists = await client.collection_exists(collection_name=collection_name)
    if exists:
        print(f"📦 Collection '{collection_name}' already exists.")
        return

    print(
        f"⚙️ Creating hybrid collection '{collection_name}' with Dense + Sparse vectors..."
    )

    # 2. Define both vector spaces
    await client.create_collection(
        collection_name=collection_name,
        vectors_config={
            # DENSE VECTOR: Configured for Cosine similarity using HNSW graph
            DENSE_VECTOR_NAME: models.VectorParams(
                size=DENSE_VECTOR_SIZE,
                distance=models.Distance.COSINE,
                hnsw_config=models.HnswConfigDiff(
                    m=16,  # Number of bidirectional links per node
                    ef_construct=100,  # Search depth during index construction
                ),
            )
        },
        sparse_vectors_config={
            # SPARSE VECTOR: Configured for BM25 with Inverse Document Frequency (IDF)
            SPARSE_VECTOR_NAME: models.SparseVectorParams(
                modifier=models.Modifier.IDF
            )
        },
    )
    print(f"✅ Hybrid collection '{collection_name}' created successfully!")