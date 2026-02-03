"""
Application settings and configuration management
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "AICC"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    TWILIO_WEBHOOK_BASE_URL: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_ORG_ID: Optional[str] = None
    WHISPER_MODEL: str = "whisper-1"
    TTS_MODEL: str = "tts-1-hd"
    TTS_VOICE: str = "alloy"

    # GPT (LLM)
    GPT_MODEL: str = "gpt-4o"
    GPT_MAX_TOKENS: int = 4096
    GPT_TEMPERATURE: float = 0.7

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str
    S3_PRESIGNED_URL_EXPIRATION: int = 3600

    # Security
    SECRET_KEY: str
    API_KEY: Optional[str] = None

    # Feature Flags
    ENABLE_CALL_RECORDING: bool = True
    ENABLE_ANALYTICS: bool = True
    MAX_CALL_DURATION: int = 3600
    MAX_CONCURRENT_CALLS: int = 100

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse ALLOWED_ORIGINS string into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
