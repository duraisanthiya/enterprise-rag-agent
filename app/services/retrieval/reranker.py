from fastembed.rerank.cross_encoder import TextCrossEncoder
from app.services.retrieval.search import SearchResult

# Load ONNX-accelerated Cross-Encoder
reranker_model = TextCrossEncoder(model_name="BAAI/bge-reranker-base")

def rerank_documents(
    query: str,
    candidates: list[SearchResult],
    top_n: int = 3,
) -> list[SearchResult]:
    """Reranks candidate search results using a cross-encoder model

    for deep query-document token interaction.
    """
    if not candidates:
        return []

    # Prepare document texts for cross-attention scoring
    doc_texts = [candidate.text for candidate in candidates]

    # Compute cross-encoder interaction scores
    scores = list(reranker_model.rerank(query, doc_texts))

    # Update candidate scores and sort descending
    for idx, candidate in enumerate(candidates):
        candidate.score = float(scores[idx])

    candidates.sort(key=lambda x: x.score, reverse=True)
    return candidates[:top_n]