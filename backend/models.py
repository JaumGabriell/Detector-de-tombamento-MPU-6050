import uuid

from sqlalchemy import Boolean, Column, BigInteger, Integer, Float, String, Uuid, Table, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

db = create_engine("sqlite:///database/database.db")

Base = declarative_base()

sensor_telegram_accounts = Table(
        "sensor_telegram_accounts",
        Base.metadata,
        Column("sensor_id", Integer, ForeignKey("sensors.id"), primary_key=True),
        Column("telegram_account_id", Integer, ForeignKey("telegram_accounts.id"), primary_key=True)
    )

class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False)
    email = Column("email", String, nullable=False, unique=True, index=True)
    password = Column("password", String, nullable=False)
    admin = Column("is_admin", Boolean, nullable=False, default=False)
    telegram_accounts = relationship("TelegramAccount", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, name, email, password, chat_id=None, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.admin = admin
        self.chat_id = chat_id

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    device_id = Column("device_id", Uuid, nullable=False, default=uuid.uuid4)
    name = Column("name", String, nullable=False)
    mqtt_username = Column("mqtt_username", String, unique=True, nullable=False)
    mqtt_enabled = Column("mqtt_enabled", Boolean, default=True, nullable=False)
    last_seen_at = Column("last_seen_at", DateTime(timezone=True), nullable=True)
    last_state = Column("last_state", String, nullable=True)
    telegram_accounts = relationship("TelegramAccount", secondary=sensor_telegram_accounts, back_populates="sensors")

    def __init__(self, name, device_id = None, mqtt_username = None, mqtt_enabled = True):
        self.name = name
        self.device_id = device_id
        self.mqtt_username = mqtt_username
        self.mqtt_enabled = mqtt_enabled

    def keys(self):
        return ["id", "device_id", "name", "mqtt_username", "mqtt_enabled", "telegram_accounts"]

    def __getitem__(self, key):
        return getattr(self, key)

class SensorAlert(Base):
    __tablename__ = "sensor_alerts"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    event_id = Column("event_id", String, unique=True, nullable=False)
    sensor_id = Column("sensor_id", Integer, ForeignKey("sensors.id"), nullable=False)
    sequence = Column("sequence", BigInteger, nullable=False)
    occurred_at = Column("occurred_at", DateTime(timezone=True), nullable=False)
    received_at = Column("received_at", DateTime(timezone=True), nullable=False)
    alert_type = Column("alert_type", String, nullable=False)
    value = Column("value", Float, nullable=False)
    threshold = Column("threshold", Float, nullable=False)

    def __init__(self, user_id, event_id, sensor_id, sequence, occurred_at, received_at, alert_type, value, threshold):
            self.user_id = user_id
            self.event_id = event_id
            self.sensor_id = sensor_id
            self.sequence = sequence 
            self.occurred_at = occurred_at
            self.received_at = received_at
            self.alert_type = alert_type
            self.value = value
            self.threshold = threshold


class TelegramAccount(Base):
    __tablename__ = "telegram_accounts"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    username = Column("username", String, nullable=True) # user's username on telegram
    chat_id = Column("chat_id", Integer, nullable=True)
    user = relationship("User", back_populates="telegram_accounts")
    sensors = relationship("Sensor", secondary=sensor_telegram_accounts, back_populates="telegram_accounts")

    def __init__(self, user_id):
        self.user_id = user_id
        
