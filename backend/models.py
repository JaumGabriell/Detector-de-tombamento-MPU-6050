import uuid

from sqlalchemy import Boolean, Column, Integer, String, Uuid, Table, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

db = create_engine("sqlite:///database/database.db")

Base = declarative_base()

sensor_users = Table(
        "sensor_users",
        Base.metadata,
        Column("sensor_id", Integer, ForeignKey("sensors.id"), primary_key=True),
        Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
    )

class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False)
    email = Column("email", String, nullable=False, unique=True, index=True)
    password = Column("password", String, nullable=False)
    admin = Column("is_admin", Boolean, nullable=False, default=False)
    telegram_account = relationship("TelegramAccount", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sensors = relationship("Sensor", secondary=sensor_users, back_populates="users")

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
    users = relationship("User", secondary=sensor_users, back_populates="sensors")

    def __init__(self, name, device_id = None):
        self.name = name
        self.device_id = device_id

    def keys(self):
        return ["id", "device_id", "name", "users"]

    def __getitem__(self, key):
        return getattr(self, key)
        
class TelegramAccount(Base):
    __tablename__ = "telegram_accounts"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False, unique=True)
    username = Column("username", String, nullable=True) # user's username on telegram
    chat_id = Column("chat_id", Integer, nullable=True, unique=True)
    user = relationship("User", back_populates="telegram_account")

    def __init__(self, user_id):
        self.user_id = user_id
        