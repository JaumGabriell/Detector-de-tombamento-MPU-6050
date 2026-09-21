from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from dependencies import get_authenticated_user, get_session
from core.telegram import get_connection_link, process_message
from models import TelegramAccount, User, sensor_telegram_accounts
from schemas.telegram_account import TelegramAccountResponse, TelegramAccountConnection, TelegramAccountListResponse

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
    pending_accounts = session.scalars(
        select(TelegramAccount).where(
            TelegramAccount.user_id == user.id,
            TelegramAccount.chat_id.is_(None),
        )
    ).all()

    if pending_accounts:
        pending_account_ids = [account.id for account in pending_accounts]
        session.execute(
            delete(sensor_telegram_accounts).where(
                sensor_telegram_accounts.c.telegram_account_id.in_(pending_account_ids)
            )
        )
        for account in pending_accounts:
            session.delete(account)
        session.flush()
    
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

@telegram_router.get("/", response_model=TelegramAccountListResponse)
def get_telegram_accounts(page: int = Query(1, ge=1), user: User = Depends(get_authenticated_user), session: Session = Depends(get_session)):
    PER_PAGE = 10
    query = session.query(TelegramAccount).filter(
        TelegramAccount.user_id == user.id,
        TelegramAccount.chat_id.is_not(None),
    )
    total = query.count()
    offset = (page - 1) * PER_PAGE
    items = query.order_by(TelegramAccount.id).offset(offset).limit(PER_PAGE).all()
    pages = (total + PER_PAGE - 1) // PER_PAGE
    
    return TelegramAccountListResponse(
        items=items,
        page=page,
        total=total,
        pages=pages,
    )

@telegram_router.get("/{telegram_account_id}", response_model=TelegramAccountResponse, status_code=status.HTTP_200_OK)
def get_telegram_account(telegram_account_id: int, user: User = Depends(get_authenticated_user), session: Session = Depends(get_session)):
    telegram_account = session.scalar(
        select(TelegramAccount).where(TelegramAccount.id == telegram_account_id)
    )

    if telegram_account is None or telegram_account.chat_id is None:
        raise HTTPException(status_code=404, detail="Conta do telegram não encontrada")

    if telegram_account.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não pode acessar esta conta do telegram")

    return telegram_account

@telegram_router.delete("/{telegram_account_id}", status_code=status.HTTP_200_OK)
def remove_telegram_account(telegram_account_id: int, user: User = Depends(get_authenticated_user), session: Session = Depends(get_session)):
    telegram_account = session.scalar(
        select(TelegramAccount)
        .where(TelegramAccount.id == telegram_account_id)
    )
     
    if telegram_account is None or telegram_account.chat_id is None:
        raise HTTPException(status_code=404, detail="Conta do telegram não vinculada")

    if telegram_account.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não pode remover esta conta do telegram")

    session.delete(telegram_account)
    session.commit()

    return {"message": "Conta do telegram desvinculada com sucesso."}
