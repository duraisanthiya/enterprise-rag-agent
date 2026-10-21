from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise RAG & Agent API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    OPENAI_API_KEY: str = Field(..., description="API Key for OpenAI/Azure provider")
    LLM_MODEL: str = Field(default="gpt-4o-mini", description="Primary chat model")
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", description="Dense embedding model")

    QDRANT_HOST: str = Field(default="localhost", description="Qdrant host address")
    QDRANT_PORT: int = Field(default=6333, description="Qdrant port")
    QDRANT_COLLECTION_NAME: str = Field(default="enterprise_knowledge_base", description="Target vector collection")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
