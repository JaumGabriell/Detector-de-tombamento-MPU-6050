import os

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from routes.auth_routes import auth_router
from routes.sensor_routes import sensor_router
from routes.telegram_routes import telegram_router
from fastapi.middleware.cors import CORSMiddleware
from core.telegram import register_telegram_webhook

from models import Base, db
from routes.auth_routes import auth_router
from routes.chat_routes import chat_router

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await register_telegram_webhook()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(sensor_router)
app.include_router(telegram_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
