import os
import httpx
from core.security import create_telegram_token, verify_telegram_token
from dependencies import Session
from sqlalchemy import select
from fastapi import HTTPException
from models import TelegramAccount

BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET")
WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")

url = f"https://t.me/{BOT_USERNAME}"

async def register_telegram_webhook():
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "url": WEBHOOK_URL,
                "secret_token": TELEGRAM_WEBHOOK_SECRET
            },
        )

        response.raise_for_status()
        return response.json()

def get_connection_link(user_id: int) -> dict:
    telegram_token = create_telegram_token(user_id)
    return {"connection_link":f"{url}?start={telegram_token}", "connection_code": telegram_token}

async def send_message(chat_id: str, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{API_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
            }
        )

async def _connect_account(message: dict, session: Session):
    """Using the recived message verifies the authenticity and associente the telegram account with the user"""
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")
    token = text.split(" ", 1)[1]
    
    user_id = verify_telegram_token(token)
    
    if user_id is None:
        await send_message(chat_id, "Acesso não autorizado. Verifique se o link ainda é válido.")
        return
        
    existing_account = session.scalar(
        select(TelegramAccount).where(
            TelegramAccount.user_id == user_id,
            TelegramAccount.chat_id == int(chat_id),
        )
    )

    if existing_account:
        await send_message(chat_id, "Este chat já está cadastrado para este usuário.")
        return

    telegram_user = message.get("from", {})
    if chat["type"] == "group":
        username = chat["title"]
    else:
        username = telegram_user["first_name"]
    
    telegram_account = session.scalar(
        select(TelegramAccount)
        .where(TelegramAccount.user_id == user_id, TelegramAccount.chat_id.is_(None))
        .order_by(TelegramAccount.id.desc())
    )

    if not telegram_account:
        await send_message(chat_id, "Ocorreu um erro interno ao registrar sua conta.")
        return

    telegram_account.chat_id = int(chat_id)
    telegram_account.username = username

    session.commit()

    await send_message(chat_id, "Conta vinculada com sucesso!")

async def process_message(request_secret: str, message: dict, session: Session):
    """Recives the message and routes it through the different commands"""
    if request_secret != TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    text = message.get("text")
    
    if not text:
        return

    chat = message.get("chat", {})
    chat_type = chat["type"]

    """if chat_type != "private":
        return"""

    if message["text"].startswith("/start ") or message["text"].startswith("/link "):
        await _connect_account(message, session)
        return

    await send_message(chat["id"], "Comando invalido.")
