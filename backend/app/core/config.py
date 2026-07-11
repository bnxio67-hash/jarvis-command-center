"""
Zentrale Konfiguration für JARVIS-Architect Backend.
Werte werden aus Umgebungsvariablen / .env geladen.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Allgemein
    APP_NAME: str = "JARVIS Command Center"
    ENV: str = "development"
    DEBUG: bool = True

    # Sicherheit
    API_KEY: str = "change-me-in-env"  # Pflichtfeld für alle mobilen Clients
    CORS_ORIGINS: list[str] = ["*"]  # Für Produktivbetrieb einschränken!

    # LLM / Tool-Calling
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-4-6"

    # Externe Dienste
    SEARCH_API_KEY: str = ""          # z.B. Brave Search / SerpAPI
    N2YO_API_KEY: str = ""            # Für Satelliten-TLE-Daten (Modul 2)

    # Telemetrie
    TELEMETRY_INTERVAL_SECONDS: float = 1.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
