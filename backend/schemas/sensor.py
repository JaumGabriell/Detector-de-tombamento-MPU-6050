from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from schemas.telegram_account import TelegramAccountResponse

class SensorPayload(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    device_id: UUID

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("O nome não pode ser vazio.")
        return name

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
    telegram_accounts: list[TelegramAccountResponse] | None

class SensorListResponse(BaseModel):
    items: list[SensorResponse]
    page: int
    total: int
    pages: int
