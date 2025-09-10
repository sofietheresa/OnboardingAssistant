# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import Optional
import logging
import os
from dotenv import load_dotenv
from .security import SecurityValidator, mask_sensitive_data

# Lade .env Datei explizit
load_dotenv()

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Postgres
    database_url: str = Field(..., description="PostgreSQL database connection URL")
    ibm_pg_ca_cert: Optional[str] = Field(None, description="Base64-encoded IBM Cloud PostgreSQL SSL certificate")

    # watsonx.ai (optional for IBM Cloud deployment with local services)
    watsonx_api_key: Optional[str] = Field(None, description="WatsonX API key (optional for local deployment)")
    watsonx_base_url: str = Field(default="https://us-south.ml.cloud.ibm.com", description="WatsonX base URL")
    embeddings_model_id: str = Field(default="ibm/granite-embedding-278m-multilingual", description="Embeddings model ID")
    llm_model_id: str = Field(default="ibm/granite-3-8b-instruct", description="LLM model ID")
    watsonx_project_id: Optional[str] = Field(None, description="WatsonX project ID")

    # Boardy API
    boardy_api_url: str = Field(default="https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/v1/ask", description="Boardy API URL")

    # Speech to Text
    speech_to_text_api_key: Optional[str] = Field(None, description="IBM Speech to Text API key")
    speech_to_text_url: str = Field(default="https://api.eu-de.speech-to-text.watson.cloud.ibm.com", description="IBM Speech to Text service URL")

    # Text to Speech
    text_to_speech_api_key: Optional[str] = Field(None, description="IBM Text to Speech API key")
    text_to_speech_url: str = Field(default="https://api.eu-de.text-to-speech.watson.cloud.ibm.com", description="IBM Text to Speech service URL")

    # CORS
    cors_origins: str = Field(default="http://localhost:5173,http://localhost:8000,https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud", description="CORS allowed origins")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Auto-reload on changes")

    # pydantic v2 Settings-Config
    model_config = SettingsConfigDict(
        env_prefix="",          # lies direkt aus ENV
        case_sensitive=False,   # env keys case-insensitive
        extra="ignore",         # ignoriere unbekannte ENV Variablen
    )

    @validator('watsonx_api_key')
    def validate_api_key(cls, v):
        if v and not SecurityValidator.validate_api_key(v):
            raise ValueError('Invalid WatsonX API key format')
        return v

    @validator('watsonx_project_id')
    def validate_project_id(cls, v):
        if v and not SecurityValidator.validate_project_id(v):
            print(f"Warning: WatsonX project ID format may be invalid: {v[:10]}...")
        return v

    @validator('database_url')
    def validate_database_url(cls, v):
        if not SecurityValidator.validate_database_url(v):
            print(f"Warning: Database URL format may be invalid: {v[:20]}...")
        return v

    @validator('ibm_pg_ca_cert')
    def validate_ssl_cert(cls, v):
        if v and not SecurityValidator.validate_ssl_certificate(v):
            print(f"Warning: SSL certificate format may be invalid")
        return v

    def get_secret_manager(self, master_key: Optional[str] = None):
        """Get secret manager instance"""
        from .security import SecretManager
        return SecretManager(master_key)

    def get_safe_database_url(self) -> str:
        """Get database URL with masked password for logging"""
        if '://' in self.database_url and '@' in self.database_url:
            # Extract parts
            parts = self.database_url.split('://', 1)
            protocol = parts[0]
            rest = parts[1]
            
            if '@' in rest:
                user_pass, host_db = rest.split('@', 1)
                if ':' in user_pass:
                    user, password = user_pass.split(':', 1)
                    masked_password = mask_sensitive_data(password)
                    safe_url = f"{protocol}://{user}:{masked_password}@{host_db}"
                else:
                    safe_url = f"{protocol}://{mask_sensitive_data(user_pass)}@{host_db}"
            else:
                safe_url = self.database_url
        else:
            safe_url = self.database_url
            
        return safe_url

    def log_configuration(self):
        """Log configuration with masked sensitive data"""
        logger.info("=== Application Configuration ===")
        logger.info(f"Database URL: {self.get_safe_database_url()}")
        logger.info(f"WatsonX API Key: {mask_sensitive_data(self.watsonx_api_key) if self.watsonx_api_key else 'Not set (using local services)'}")
        logger.info(f"WatsonX Project ID: {mask_sensitive_data(self.watsonx_project_id) if self.watsonx_project_id else 'Not set'}")
        logger.info(f"WatsonX Base URL: {self.watsonx_base_url}")
        logger.info(f"Embeddings Model: {self.embeddings_model_id}")
        logger.info(f"LLM Model: {self.llm_model_id}")
        logger.info(f"Boardy API URL: {self.boardy_api_url}")
        logger.info(f"Speech to Text API Key: {mask_sensitive_data(self.speech_to_text_api_key) if self.speech_to_text_api_key else 'Not set'}")
        logger.info(f"Speech to Text URL: {self.speech_to_text_url}")
        logger.info(f"Text to Speech API Key: {mask_sensitive_data(self.text_to_speech_api_key) if self.text_to_speech_api_key else 'Not set'}")
        logger.info(f"Text to Speech URL: {self.text_to_speech_url}")
        logger.info(f"CORS Origins: {self.cors_origins}")
        logger.info(f"SSL Certificate: {'Configured' if self.ibm_pg_ca_cert else 'Not configured'}")
        logger.info("================================")

settings = Settings()
