from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.security import create_jwt_token, hash_password, verify_password, verify_token
from dependencies import get_session, get_authenticated_user
from models import User
from schemas.auth import LoginRequest, Token, UserCreate, UserResponse
from datetime import timedelta

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session: Session = Depends(get_session)):
    email = payload.email.lower()
    user = session.scalar(select(User).where(User.email == email))

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail.",
        )

    new_user = User(payload.name, email, hash_password(payload.password))
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail.",
        )

    return new_user


@auth_router.post("/login", response_model=Token)
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.email == payload.email.lower()))

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_jwt_token(str(user.id))
    refresh_token = create_jwt_token(str(user.id), timedelta(days=1))

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

@auth_router.post("/login-form", response_model=Token)
def login_form(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.email == form.username.lower()))

    if not user or not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_jwt_token(str(user.id))
    refresh_token = create_jwt_token(str(user.id), timedelta(days=1))

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

@auth_router.get("/refresh", response_model=Token)
def use_refresh_token(user: User = Depends(get_authenticated_user)):
    access_token = create_jwt_token(str(user.id))
    refresh_token = create_jwt_token(str(user.id), timedelta(days=1))

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )