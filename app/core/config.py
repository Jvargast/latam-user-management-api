from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# La raíz del proyecto con .env
ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "LATAM User Management API"
    app_version: str = "1.0.0"
    environment: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://latam:latam@localhost:5434/users_db"

    # Cada entorno puede traer o no claves extra sin romper la carga
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    # Una sola instancia de configuración para el ciclo de vida
    return Settings()


settings = get_settings()
