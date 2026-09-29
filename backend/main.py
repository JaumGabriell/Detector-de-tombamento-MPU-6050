import os
import asyncio

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from routes.auth_routes import auth_router
from routes.chat_routes import chat_router
from routes.sensor_routes import sensor_router
from routes.telegram_routes import telegram_router
from fastapi.middleware.cors import CORSMiddleware
from core.telegram import register_telegram_webhook
from core.config import get_settings
from mqtt.consumer import MQTTConsumer

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

# Task global do MQTT
mqtt_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_task
    
    # Registra webhook do Telegram (opcional)
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if telegram_token:
        try:
            await register_telegram_webhook()
        except Exception as e:
            print(f"⚠️  Webhook Telegram não configurado: {e}")
    
    # Inicia MQTT Consumer em background
    try:
        settings = get_settings()
        consumer = MQTTConsumer(settings)
        mqtt_task = asyncio.create_task(consumer.run())
        print("✅ MQTT Consumer iniciado")
    except Exception as e:
        print(f"⚠️  MQTT Consumer não iniciado: {e}")
    
    yield
    
    # Cleanup
    if mqtt_task:
        mqtt_task.cancel()
        try:
            await mqtt_task
        except asyncio.CancelledError:
            pass

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(chat_router)
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
