from datetime import timezone

from fastapi import HTTPException
from models import Sensor, SensorAlert


def filter_sensors(query, name=None, device_id=None, last_state=None, mqtt_enabled=None):
    if name:
        query = query.filter(Sensor.name.icontains(name, autoescape=True))
    if device_id is not None:
        query = query.filter(Sensor.device_id == device_id)
    if last_state == "unknown":
        query = query.filter(Sensor.last_state.is_(None))
    elif last_state is not None:
        query = query.filter(Sensor.last_state == last_state)
    if mqtt_enabled is not None:
        query = query.filter(Sensor.mqtt_enabled == mqtt_enabled)
    return query


def filter_alerts(query, sensor_id=None, alert_type=None, start=None, end=None):
    for value in (start, end):
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise HTTPException(status_code=422, detail="As datas devem incluir fuso horário")
    start = start.astimezone(timezone.utc).replace(tzinfo=None) if start else None
    end = end.astimezone(timezone.utc).replace(tzinfo=None) if end else None
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="A data inicial deve ser anterior à data final")
    if sensor_id is not None:
        query = query.filter(SensorAlert.sensor_id == sensor_id)
    if alert_type is not None:
        query = query.filter(SensorAlert.alert_type == alert_type)
    if start is not None:
        query = query.filter(SensorAlert.occurred_at >= start)
    if end is not None:
        query = query.filter(SensorAlert.occurred_at <= end)
    return query
