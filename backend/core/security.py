import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException, status
from jose import jwt

ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def _get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key or len(secret_key) < 32:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SECRET_KEY deve ser configurada com ao menos 32 caracteres.",
        )
    return secret_key


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_jwt_token(subject: str, duration: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    expires_at = datetime.now(timezone.utc) + duration
    return jwt.encode({"sub": subject, "exp": expires_at}, _get_secret_key(), algorithm=ALGORITHM)


def verify_token(token):
    return jwt.decode(token, _get_secret_key(), algorithms=ALGORITHM)