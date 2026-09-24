from datetime import datetime, timezone

from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from models import Sensor
from models import SensorAlert
from mqtt.schemas import AlertMessage


async def process_alert(session_factory: async_sessionmaker[AsyncSession], sensor_id: int, message: AlertMessage) -> bool:
    async with session_factory() as session:
        sensor = await session.get(
            Sensor,
            sensor_id,
        )

        if sensor is None:
            raise ValueError(
                f"Unknown sensor: {sensor_id}"
            )

        now = datetime.now(timezone.utc)

        statement = (
            sqlite_insert(SensorAlert)
            .values(
                event_id=str(message.event_id),
                sensor_id=sensor_id,
                occurred_at=message.occurred_at,
                received_at=now,
                alert_type=message.type,
                x=message.x,
                y=message.y,
                z=message.z,
                inclination=message.inclination,
            )
            .on_conflict_do_nothing(
                index_elements=["event_id"]
            )
        )

        result = await session.execute(statement)

        sensor.last_seen_at = now
        sensor.last_state = "online"

        await session.commit()

        return result.rowcount == 1
