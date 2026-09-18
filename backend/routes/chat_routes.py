from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from dependencies import get_session, get_authenticated_user
from models import User
from schemas.auth import ChatIdUpdate, UserResponse


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
    user.chat_id = payload.chat_id

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
