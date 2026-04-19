from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    # LLM_MODEL: str = "mistral:7b"
    LLM_MODEL: str = "qwen2.5:1.5b"

    EMBEDDING_MODEL: str = "nomic-embed-text"

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "course_kb"

    REDIS_URL: str = "redis://localhost:6379/0"
    SESSION_TTL_HOURS: int = 24

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    SEARCH_TOP_K: int = 3
    RELEVANCE_THRESHOLD: float = 0.6

    API_PREFIX: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()