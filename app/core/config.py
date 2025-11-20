# app/core/config.py

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- LLM / API settings ---
    openai_api_key: str | None = None          # maps from OPENAI_API_KEY
    model_provider: str = "ollama"             # maps from MODEL_PROVIDER
    model_name: str = "mistral"                # maps from MODEL_NAME

    # --- Embeddings / vectorstore ---
    embeddings_model: str = "all-MiniLM-L6-v2" # maps from EMBEDDINGS_MODEL

    # --- Backend URL (used by eval / UI helpers etc.) ---
    backend_url: str = "http://127.0.0.1:8000" # maps from BACKEND_URL

    # --- Evaluation defaults ---
    eval_top_k: int = 8                        # maps from EVAL_TOP_K
    eval_mode: str = "hybrid"                  # maps from EVAL_MODE
    eval_questions_file: str = "questions.txt" # maps from EVAL_QUESTIONS_FILE
    eval_models_file: str = "configs/models.json"  # maps from EVAL_MODELS_FILE

    # --- OCR support ---
    enable_ocr: bool = True                    # maps from ENABLE_OCR
    ocr_lang: str = "eng"                      # maps from OCR_LANG
    tesseract_cmd: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # TESSERACT_CMD

    # --- Chroma telemetry ---
    chroma_telemetry_enabled: bool = False     # CHROMA_TELEMETRY_ENABLED

    # BaseSettings config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",        # IMPORTANT: ignore any other env vars
        case_sensitive=False,  # ENV names not case-sensitive
    )


settings = Settings()
