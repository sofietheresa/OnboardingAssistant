# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Postgres
    database_url: str

    # watsonx.ai
    watsonx_api_key: str
    watsonx_base_url: str
    embeddings_model_id: str
    llm_model_id: str
    watsonx_project_id: str = ""

    # pydantic v2 Settings-Config
    model_config = SettingsConfigDict(
        env_prefix="",          # lies direkt aus ENV
        case_sensitive=False,   # env keys case-insensitive
        extra="ignore",         # ignoriere unbekannte ENV Variablen
    )

settings = Settings()
