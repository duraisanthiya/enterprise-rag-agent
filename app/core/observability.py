import os
from langfuse.langchain import CallbackHandler
from app.core.config import settings

def get_langfuse_callback(
    trace_name: str = "rag_query",
) -> CallbackHandler | None:
    """Returns a Langfuse callback handler for LangGraph tracing

    if credentials are configured, otherwise returns None safely.
    """
    if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
        # Langfuse v3 reads credentials from standard environment variables
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
        os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
        os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST
        return CallbackHandler()
    return None