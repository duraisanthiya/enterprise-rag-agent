class EnterpriseRAGException(Exception):
    """Base exception for all domain-specific errors."""

    def __init__(self, message: str, error_code: str = "INTERNAL_RAG_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class VectorStoreUnavailableError(EnterpriseRAGException):
    """Raised when the vector database is unreachable."""

    def __init__(self, message: str = "Vector database is currently unreachable."):
        super().__init__(message, error_code="VECTOR_STORE_UNAVAILABLE")


class LLMProviderError(EnterpriseRAGException):
    """Raised when external LLM generation fails or times out."""

    def __init__(self, message: str = "LLM provider failed to generate a response."):
        super().__init__(message, error_code="LLM_PROVIDER_ERROR")
