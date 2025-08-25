from pydantic import BaseSettings

class Settings(BaseSettings):
    # Postgres
    database_url: str

    # watsonx.ai
    watsonx_api_key: str
    watsonx_base_url: str
    embeddings_model_id: str
    llm_model_id: str
    watsonx_project_id: str = ""

    class Config:
        env_prefix = ""    # liest direkt aus ENV
        case_sensitive = False

settings = Settings()
