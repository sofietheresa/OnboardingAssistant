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

    # Speech to Text
    speech_to_text_api_key: Optional[str] = Field(None, description="IBM Speech to Text API key")
    speech_to_text_url: str = Field(default="https://api.eu-de.speech-to-text.watson.cloud.ibm.com", description="IBM Speech to Text service URL")

    # Text to Speech
    text_to_speech_api_key: Optional[str] = Field(None, description="IBM Text to Speech API key")
    text_to_speech_url: str = Field(default="https://api.eu-de.text-to-speech.watson.cloud.ibm.com", description="IBM Text to Speech service URL")


settings = Settings()