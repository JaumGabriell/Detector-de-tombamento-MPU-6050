from fastapi import APIRouter, Depends
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_session, get_authenticated_user
from models import User, TelegramAccount, Sensor, sensor_telegram_accounts
from schemas.auth import ChatIdUpdate
from schemas.user import UserResponse


chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@chat_router.put("/chat_id", response_model=UserResponse)
def update_chat_id(
    payload: ChatIdUpdate,
    user: User = Depends(get_authenticated_user),
    session: Session = Depends(get_session)
):
    new_chat_id = str(payload.chat_id)

    # Impede que duas contas usem o mesmo chat_id.
    existing = session.scalar(
        select(TelegramAccount).where(
            TelegramAccount.chat_id == payload.chat_id
        )
    )

    if existing and existing.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este chat ID já está vinculado a outro usuário.",
        )

    try:
        current_chat_id = int(user.chat_id) if user.chat_id is not None else None
    except (TypeError, ValueError):
        current_chat_id = None

    account = session.scalar(
        select(TelegramAccount).where(
            TelegramAccount.user_id == user.id,
            TelegramAccount.chat_id == current_chat_id,
        )
    )

    if account:
        if not existing:
            account.chat_id = payload.chat_id
    elif not existing:
        telegram_account = TelegramAccount(user.id)
        telegram_account.chat_id = payload.chat_id
        session.add(telegram_account)
        session.flush()
        
        # Vincula a todos os sensores existentes automaticamente
        sensors = session.scalars(select(Sensor)).all()
        for sensor in sensors:
            # Verifica se já não está vinculado
            already_linked = session.execute(
                select(sensor_telegram_accounts).where(
                    sensor_telegram_accounts.c.sensor_id == sensor.id,
                    sensor_telegram_accounts.c.telegram_account_id == telegram_account.id
                )
            ).first()
            if not already_linked:
                sensor.telegram_accounts.append(telegram_account)

    # Mantém o campo legado sincronizado com a conta do Telegram.
    user.chat_id = new_chat_id
    session.commit()
    session.refresh(user)

    return user


@chat_router.get("/chats_id")
def get_chat_ids(
    user: User = Depends(get_authenticated_user),
    session: Session = Depends(get_session)
):
    # Admin pode visualizar os chat_ids de todos os usuários
    if user.admin:
        users = session.scalars(
            select(User).where(User.chat_id.isnot(None))
        ).all()

        return [
            {
                "user_id": current_user.id,
                "chat_id": current_user.chat_id
            }
            for current_user in users
        ]

    if user.chat_id is None:
        return []
    # Usuário comum pode visualizar somente o próprio chat_id
    return [
        {
            "user_id": user.id,
            "chat_id": user.chat_id
        }
    ]
