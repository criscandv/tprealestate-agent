from typing import Optional

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # Aplicacion
    APP_NAME: str = "TPRE Agent AI"
    APP_DESCRIPTION: str = "API de IA (agente) para Top Premium Real Estate"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/v1"
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"

    # Entorno
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Base de datos del agente
    POSTGRES_SERVER: str = "tprealestate-agent-db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "tprealestate_agent"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> str:
        if isinstance(v, str) and v:
            return v
        d = info.data
        return (
            f"postgresql+psycopg2://{d.get('POSTGRES_USER')}:{d.get('POSTGRES_PASSWORD')}"
            f"@{d.get('POSTGRES_SERVER')}:{d.get('POSTGRES_PORT')}/{d.get('POSTGRES_DB')}"
        )

    # Autenticacion entrante al agente
    ALGORITHM: str = "HS256"
    # API key de servicio que envian los frontends/procesos al agente
    SERVICE_API_KEY: str = ""
    # Secreto con el que Django firma sus JWT (para verificarlos en el agente)
    DJANGO_JWT_SECRET: str = ""

    # Conexion con la API de Django (CRM)
    DJANGO_API_BASE_URL: str = "http://host.docker.internal:8000/v1"
    # API key de servicio que el agente envia a Django (acciones anonimas/sistema)
    DJANGO_SERVICE_API_KEY: str = ""

    # OpenAI (LLM principal, swappable)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Langfuse (observabilidad)
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = ""

    # Redis / Celery (tareas en segundo plano)
    REDIS_URL: str = "redis://tprealestate-agent-redis:6379/0"
    CELERY_BROKER_URL: str = "redis://tprealestate-agent-redis:6379/1"


settings = Settings()
