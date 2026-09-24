from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from schemas.telegram_account import TelegramAccountResponse

class SensorPayload(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    device_id: UUID
    mqtt_username: str = Field(min_length=1, max_length=100)
    mqtt_enabled: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("O nome não pode ser vazio.")
        return name

    @field_validator("mqtt_username")
    @classmethod
    def validate_mqtt_username(cls, value: str) -> str:
        username = value.strip()
        if not username:
            raise ValueError("mqtt_username cannot be empty.")
        return username

    @field_validator("device_id")
    @classmethod
    def validate_sensor_id(cls, value: UUID) -> UUID:
        if value.version != 4:
            raise ValueError("O UUID deve ser versão 4.")
        return value

class SensorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    device_id: UUID
    mqtt_username: str
    mqtt_enabled: bool
    last_seen_at: datetime | None
    last_state: str | None
    telegram_accounts: list[TelegramAccountResponse] | None

class SensorListResponse(BaseModel):
    items: list[SensorResponse]
    page: int
    total: int
    pages: int
