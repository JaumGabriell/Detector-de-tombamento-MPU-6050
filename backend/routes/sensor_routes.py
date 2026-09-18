from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError


from dependencies import get_authenticated_user, get_session
from models import Sensor, User
from schemas.sensor import SensorPayload, SensorResponse, SensorListResponse

sensor_router = APIRouter(prefix="/sensor", tags=["Sensors"])

@sensor_router.post("/", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor(payload: SensorPayload, session: Session = Depends(get_session)):
    new_sensor = Sensor(payload.name, payload.device_id)

    session.add(new_sensor)
    session.commit()
    session.refresh(new_sensor)

    response = dict(new_sensor)
    response["telegram_accounts"] = None

    return response

@sensor_router.get("/{sensor_id}", response_model=SensorResponse, status_code=status.HTTP_200_OK)
async def get_sensor(sensor_id: int, session: Session = Depends(get_session)):
    sensor = session.query(Sensor).options(selectinload(Sensor.users).selectinload(User.telegram_account)).filter(Sensor.id == sensor_id).first()

    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    return SensorResponse(
        id=sensor.id,
        name=sensor.name,
        device_id=sensor.device_id,
        telegram_accounts=[user.telegram_account for user in sensor.users if user.telegram_account is not None and user.telegram_account.chat_id is not None]
    )

@sensor_router.get("/", response_model=SensorListResponse, status_code=status.HTTP_200_OK)
def get_sensors(page: int = Query(1, ge=1), session: Session = Depends(get_session)):
    PER_PAGE = 10
    total = session.query(Sensor).count()
    offset = (page - 1) * PER_PAGE

    sensors = (session.query(Sensor).options(selectinload(Sensor.users).selectinload(User.telegram_account)).order_by(Sensor.id).offset(offset).limit(PER_PAGE).all())

    pages = (total + PER_PAGE - 1) // PER_PAGE

    items = [
        SensorResponse(
            id=sensor.id,
            name=sensor.name,
            device_id=sensor.device_id,
            telegram_accounts=[user.telegram_account for user in sensor.users if user.telegram_account is not None and user.telegram_account.chat_id is not None]
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
async def update_sensor(sensor_id: int, payload: SensorPayload, session: Session = Depends(get_session)):
    sensor = session.query(Sensor).filter(Sensor.id == sensor_id).first()

    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    sensor.name = payload.name
    sensor.device_id = payload.device_id

    session.commit()
    session.refresh(sensor)
    return sensor

@sensor_router.post("/link/{sensor_id}/{user_id}", response_model=SensorResponse, status_code=status.HTTP_200_OK)
async def link_to_user(sensor_id: int, user_id: int, session: Session = Depends(get_session)):
    sensor = session.query(Sensor).filter(Sensor.id == sensor_id).first()
    user = session.query(User).filter(User.id == user_id).first()
    
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    if user is None:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    try:
        sensor.users.append(user)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A conta ja esta associada ao sensor",
        )
    sensor = session.query(Sensor).options(selectinload(Sensor.users).selectinload(User.telegram_account)).filter(Sensor.id == sensor_id).first()

    return SensorResponse(
        id=sensor.id,
        name=sensor.name,
        device_id=sensor.device_id,
        telegram_accounts=[user.telegram_account for user in sensor.users if user.telegram_account is not None and user.telegram_account.chat_id is not None]
    )
    

@sensor_router.delete("/{sensor_id}", status_code=status.HTTP_200_OK)
async def delete_sensor(sensor_id: int, session: Session = Depends(get_session)):
    sensor = session.query(Sensor).filter(Sensor.id == sensor_id).first()
    
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    session.delete(sensor)
    session.commit()

    return {"message": "Sensor deletado com sucesso."}


    
    