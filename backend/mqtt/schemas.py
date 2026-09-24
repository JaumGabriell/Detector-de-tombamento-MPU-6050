from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class AlertMessage(BaseModel):
    schema_version: int
    event_id: UUID
    occurred_at: datetime
    type: str
    x: float
    y: float
    z: float
    inclination: float


class StateMessage(BaseModel):
    schema_version: int
    state: str
    occurred_at: datetime
