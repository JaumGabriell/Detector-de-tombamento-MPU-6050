from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dependencies import get_authenticated_user, get_session
from core.telegram import get_connection_link, process_message
from models import TelegramAccount, User
from schemas.telegram_account import TelegramAccountResponse, TelegramAccountConnection

telegram_router = APIRouter(prefix="/telegram", tags=["Telegram"])

@telegram_router.post("/webhook")
async def on_message(request: Request, session: Session = Depends(get_session)):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    update = await request.json()

    message = update.get("message")

    if not message:
        return {"ok": True}

    await process_message(secret, message, session)

    return {"ok": True}


@telegram_router.post("/", response_model=TelegramAccountConnection, status_code=status.HTTP_200_OK)
def connect_telegram_account(user: User = Depends(get_authenticated_user), session: Session = Depends(get_session)):
    telegram_account = session.scalar(select(TelegramAccount).where(TelegramAccount.user_id == user.id))

    # deletes the previus user telegram account
    if telegram_account:
        session.delete(telegram_account)
        session.commit()
    
    new_account = TelegramAccount(user.id)

    try:
        session.add(new_account)
        session.commit()
        session.refresh(new_account)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Voce ja tem uma conta de telegram.",
                )

    return {"connection_link": get_connection_link(user.id)}

@telegram_router.get("/", response_model=TelegramAccountResponse)
def get_telegram_account(user: User = Depends(get_authenticated_user), session: Session = Depends(get_session)):
    telegram_account = session.scalar(select(TelegramAccount).where(TelegramAccount.user_id == user.id))

    if telegram_account is None or telegram_account.chat_id is None:
            raise HTTPException(status_code=404, detail="Conta do telegram não vinculada")
    
    return telegram_account

@telegram_router.delete("/", status_code=status.HTTP_200_OK)
def remove_telegram_account(user: User = Depends(get_authenticated_user), session: Session = Depends(get_session)):
    telegram_account = session.scalar(select(TelegramAccount).where(TelegramAccount.user_id == user.id))
     
    if telegram_account is None or telegram_account.chat_id is None:
        raise HTTPException(status_code=404, detail="Conta do telegram não vinculada")

    session.delete(telegram_account)
    session.commit()

    return {"message": "Conta do telegram desvinculada com sucesso."}