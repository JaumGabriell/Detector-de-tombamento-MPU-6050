from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SensorAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: UUID
    sensor_id: int
    occurred_at: datetime
    received_at: datetime
    alert_type: str
    x: float
    y: float
    z: float
    inclination: float


class SensorAlertListResponse(BaseModel):
    items: list[SensorAlertResponse]
    page: int
    total: int
    pages: int
