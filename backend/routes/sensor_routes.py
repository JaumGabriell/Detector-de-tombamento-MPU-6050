from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError


from dependencies import get_authenticated_user, get_session
from models import Sensor, SensorAlert, TelegramAccount, User
from schemas.sensor import SensorPayload, SensorResponse, SensorListResponse
from schemas.sensor_alert import SensorAlertResponse, SensorAlertListResponse

sensor_router = APIRouter(prefix="/sensor", tags=["Sensors"])

@sensor_router.post("/", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor(payload: SensorPayload, session: Session = Depends(get_session), user: User = Depends(get_authenticated_user)):
    new_sensor = Sensor(
        payload.name,
        payload.device_id,
        payload.mqtt_username,
        payload.mqtt_enabled,
    )

    try:
        session.add(new_sensor)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este username MQTT ja esta associado a outro sensor.",
        )
    session.refresh(new_sensor)

    response = dict(new_sensor)
    response["telegram_accounts"] = None

    return response

@sensor_router.get("/{sensor_id}", response_model=SensorResponse, status_code=status.HTTP_200_OK)
async def get_sensor(sensor_id: int, session: Session = Depends(get_session), user: User = Depends(get_authenticated_user)):
    sensor = session.query(Sensor).options(selectinload(Sensor.telegram_accounts)).filter(Sensor.id == sensor_id).first()

    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    return SensorResponse(
        id=sensor.id,
        name=sensor.name,
        device_id=sensor.device_id,
        mqtt_username=sensor.mqtt_username,
        mqtt_enabled=sensor.mqtt_enabled,
        telegram_accounts=[account for account in sensor.telegram_accounts if account.chat_id is not None]
    )

@sensor_router.get("/{sensor_id}/alert/{alert_id}", response_model=SensorAlertResponse, status_code=status.HTTP_200_OK)
async def get_sensor_alert(sensor_id: int, alert_id: int, session: Session = Depends(get_session), user: User = Depends(get_authenticated_user)):
    sensor = session.query(Sensor).filter(Sensor.id == sensor_id).first()

    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor nÃ£o encontrado")

    alert = session.query(SensorAlert).filter(
        SensorAlert.id == alert_id,
        SensorAlert.sensor_id == sensor_id,
    ).first()

    if alert is None:
        raise HTTPException(status_code=404, detail="Alerta nÃ£o encontrado")

    return alert

@sensor_router.get("/{sensor_id}/alert", response_model=SensorAlertListResponse, status_code=status.HTTP_200_OK)
def get_sensor_alerts(sensor_id: int, page: int = Query(1, ge=1), session: Session = Depends(get_session), user: User = Depends(get_authenticated_user)):
    sensor = session.query(Sensor).filter(Sensor.id == sensor_id).first()

    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor nÃ£o encontrado")

    PER_PAGE = 10
    query = session.query(SensorAlert).filter(SensorAlert.sensor_id == sensor_id)
    total = query.count()
    offset = (page - 1) * PER_PAGE

    alerts = (query.order_by(SensorAlert.occurred_at.desc()).offset(offset).limit(PER_PAGE).all())

    pages = (total + PER_PAGE - 1) // PER_PAGE

    return SensorAlertListResponse(
        items=alerts,
        page=page,
        total=total,
        pages=pages
    )

@sensor_router.get("/", response_model=SensorListResponse, status_code=status.HTTP_200_OK)
def get_sensors(page: int = Query(1, ge=1), session: Session = Depends(get_session), user: User = Depends(get_authenticated_user)):
    PER_PAGE = 10
    total = session.query(Sensor).count()
    offset = (page - 1) * PER_PAGE

    sensors = (session.query(Sensor).options(selectinload(Sensor.telegram_accounts)).order_by(Sensor.id).offset(offset).limit(PER_PAGE).all())

    pages = (total + PER_PAGE - 1) // PER_PAGE

    items = [
        SensorResponse(
            id=sensor.id,
            name=sensor.name,
            device_id=sensor.device_id,
            mqtt_username=sensor.mqtt_username,
            mqtt_enabled=sensor.mqtt_enabled,
            telegram_accounts=[account for account in sensor.telegram_accounts if account.chat_id is not None]
        )
        for sensor in sensors
    ]

    return SensorListResponse(
        items=items,
        page=page,
        total=total,
        pages=pages
    )

@sensor_router.put("/{sensor_id}", response_model=SensorResponse, status_code=status.HTTP_200_OK)
async def update_sensor(sensor_id: int, payload: SensorPayload, session: Session = Depends(get_session), user: User = Depends(get_authenticated_user)):
    sensor = session.query(Sensor).filter(Sensor.id == sensor_id).first()

    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    sensor.name = payload.name
    sensor.device_id = payload.device_id
    sensor.mqtt_username = payload.mqtt_username
    sensor.mqtt_enabled = payload.mqtt_enabled

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este username MQTT ja esta associado a outro sensor.",
        )
    session.refresh(sensor)
    return sensor

@sensor_router.post("/link/{sensor_id}/{telegram_account_id}", response_model=SensorResponse, status_code=status.HTTP_200_OK)
async def link_to_telegram_account(sensor_id: int, telegram_account_id: int, session: Session = Depends(get_session), user: User = Depends(get_authenticated_user)):
    sensor = session.query(Sensor).filter(Sensor.id == sensor_id).first()
    telegram_account = session.query(TelegramAccount).filter(TelegramAccount.id == telegram_account_id).first()
    
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    if telegram_account is None:
        raise HTTPException(status_code=404, detail="Conta do telegram não encontrada")
    existing_chat = session.query(TelegramAccount).join(TelegramAccount.sensors).filter(
        Sensor.id == sensor_id,
        TelegramAccount.chat_id == telegram_account.chat_id,
        TelegramAccount.chat_id.is_not(None),
    ).first()

    if existing_chat is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este chat já foi vinculado a este sensor por outro usuário.",
        )

    try:
        sensor.telegram_accounts.append(telegram_account)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A conta ja esta associada ao sensor",
        )
    sensor = session.query(Sensor).options(selectinload(Sensor.telegram_accounts)).filter(Sensor.id == sensor_id).first()

    return SensorResponse(
        id=sensor.id,
        name=sensor.name,
        device_id=sensor.device_id,
        mqtt_username=sensor.mqtt_username,
        mqtt_enabled=sensor.mqtt_enabled,
        telegram_accounts=[account for account in sensor.telegram_accounts if account.chat_id is not None]
    )
    

@sensor_router.delete("/{sensor_id}", status_code=status.HTTP_200_OK)
async def delete_sensor(sensor_id: int, session: Session = Depends(get_session), user: User = Depends(get_authenticated_user)):
    sensor = session.query(Sensor).filter(Sensor.id == sensor_id).first()
    
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    session.delete(sensor)
    session.commit()

    return {"message": "Sensor deletado com sucesso."}

@sensor_router.delete("/{sensor_id}/alert/{alert_id}", status_code=status.HTTP_200_OK)
async def delete_sensor_alert(sensor_id: int, alert_id: int, session: Session = Depends(get_session), user: User = Depends(get_authenticated_user)):
    sensor = session.query(Sensor).filter(Sensor.id == sensor_id).first()

    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor nÃ£o encontrado")

    alert = session.query(SensorAlert).filter(
        SensorAlert.id == alert_id,
        SensorAlert.sensor_id == sensor_id,
    ).first()

    if alert is None:
        raise HTTPException(status_code=404, detail="Alerta nÃ£o encontrado")

    session.delete(alert)
    session.commit()

    return {"message": "Alerta deletado com sucesso."}


    
    
