import csv
from datetime import datetime
from io import StringIO
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session, selectinload

from dependencies import get_admin_user, get_session
from models import Sensor, SensorAlert, User
from schemas.sensor_alert import SensorAlertListResponse
from schemas.telegram_account import TelegramAccountResponse
from schemas.user import UserAdminUpdate, UserResponse
from services.admin_queries import filter_alerts, filter_sensors

admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_admin_user)])


@admin_router.patch("/users/{user_id}/admin", response_model=UserResponse)
def update_user_admin(user_id: int, payload: UserAdminUpdate, session: Session = Depends(get_session), admin: User = Depends(get_admin_user)):
    if user_id == admin.id:
        raise HTTPException(status_code=403, detail="Você não pode alterar seu próprio perfil de administrador")
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.admin = payload.admin
    session.commit()
    session.refresh(user)
    return user


class SensorFilters:
    def __init__(self, name: str | None = None, device_id: UUID | None = None,
                 last_state: Literal["online", "offline", "unknown"] | None = None,
                 mqtt_enabled: bool | None = None):
        self.name = name
        self.device_id = device_id
        self.last_state = last_state
        self.mqtt_enabled = mqtt_enabled

    def apply(self, query):
        return filter_sensors(query, self.name, self.device_id, self.last_state, self.mqtt_enabled)


class AlertFilters:
    def __init__(self, sensor_id: int | None = Query(None, ge=1), alert_type: str | None = None,
                 start: datetime | None = None, end: datetime | None = None):
        self.sensor_id = sensor_id
        self.alert_type = alert_type
        self.start = start
        self.end = end

    def apply(self, query):
        return filter_alerts(query, self.sensor_id, self.alert_type, self.start, self.end)


@admin_router.get("/alerts", response_model=SensorAlertListResponse)
def list_alerts(page: int = Query(1, ge=1), filters: AlertFilters = Depends(), session: Session = Depends(get_session)):
    per_page = 10
    query = filters.apply(session.query(SensorAlert))
    total = query.count()
    items = query.order_by(SensorAlert.occurred_at.desc(), SensorAlert.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return SensorAlertListResponse(items=items, page=page, total=total, pages=(total + per_page - 1) // per_page)


@admin_router.get("/sensors/{sensor_id}/telegram-accounts", response_model=list[TelegramAccountResponse])
def list_sensor_accounts(sensor_id: int, session: Session = Depends(get_session)):
    sensor = session.query(Sensor).options(selectinload(Sensor.telegram_accounts)).filter(Sensor.id == sensor_id).first()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")
    return [account for account in sensor.telegram_accounts if account.chat_id is not None]


def csv_response(filename, columns, rows):
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([
            "'" + value if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")) else value
            for value in row
        ])
    return Response(content="\ufeff" + output.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@admin_router.get("/reports/sensors")
def export_sensors(filters: SensorFilters = Depends(), session: Session = Depends(get_session)):
    sensors = filters.apply(session.query(Sensor)).order_by(Sensor.id).all()
    columns = ("id", "name", "device_id", "mqtt_username", "mqtt_enabled", "last_seen_at", "last_state")
    return csv_response("sensores.csv", columns, ([getattr(sensor, column) for column in columns] for sensor in sensors))


@admin_router.get("/reports/alerts")
def export_alerts(filters: AlertFilters = Depends(), session: Session = Depends(get_session)):
    alerts = filters.apply(session.query(SensorAlert)).order_by(SensorAlert.occurred_at.desc(), SensorAlert.id.desc()).all()
    columns = ("id", "event_id", "sensor_id", "occurred_at", "received_at", "alert_type", "x", "y", "z", "inclination")
    return csv_response("alertas.csv", columns, ([getattr(alert, column) for column in columns] for alert in alerts))
