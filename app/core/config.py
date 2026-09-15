from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vellei AI Interview Assessment"
    llm_enabled: bool = True
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2"
    database_url: str = "sqlite:///./data/vellei.db"
    max_transcript_chars: int = 100_000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
