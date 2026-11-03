from datetime import datetime
from typing import Literal, Optional
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
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class StateMessage(BaseModel):
    schema_version: int
    state: Literal["online", "offline"]
