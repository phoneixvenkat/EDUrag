from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    allowed_origins: str = "http://localhost:3000"

    data_dir: str = "./data"
    upload_dir: str = "./data/uploads"
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection: str = "docs_default"

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_batch_size: int = 64

    max_chunk_tokens: int = 900
    chunk_overlap: int = 120

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
