import os

from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

db = create_engine("sqlite:///database.db")

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False)
    email = Column("email", String, nullable=False, unique=True, index=True)
    password = Column("password", String, nullable=False)
    admin = Column("is_admin", Boolean, nullable=False, default=False)
    chat_id = Column("chat_id", String, nullable=True, default=None)

    def __init__(self, name, email, password, chat_id=None, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.admin = admin
        self.chat_id = chat_id
