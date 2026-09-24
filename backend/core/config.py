from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./database/database.db"

    MQTT_HOST: str
    MQTT_PORT: int = 443

    MQTT_USERNAME: str
    MQTT_PASSWORD: str

    MQTT_CLIENT_ID: str = "sensor-backend-ingestor"

    MQTT_KEEPALIVE: int = 60
    MQTT_SESSION_EXPIRY: int = 86400

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()