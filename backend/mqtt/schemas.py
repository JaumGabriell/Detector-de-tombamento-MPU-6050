from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

class AlertMessage(BaseModel):
    schema_version: int
    event_id: UUID
    sequence: int = Field(ge=0)
    occurred_at: datetime
    type: str
    value: float
    threshold: float


class StateMessage(BaseModel):
    schema_version: int
    state: str
    occurred_at: datetime