import os
import base64
import hashlib
import hmac
import time
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import JWTError, jwt

ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
TELEGRAM_TOKEN_VERSION = 1
TELEGRAM_TOKEN_TTL = 180  # seconds

def _get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key or len(secret_key) < 32:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return secret_key

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_jwt_token(
    subject: str,
    duration: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    token_type: str = "access",
) -> str:
    expires_at = datetime.now(timezone.utc) + duration
    payload = {
        "sub": subject,
        "exp": expires_at,
        "type": token_type,
    }

    return jwt.encode(payload, _get_secret_key(), algorithm=ALGORITHM)

def verify_token(token, expected_type: str = "access"):
    decoded_token = jwt.decode(token, _get_secret_key(), algorithms=ALGORITHM)
    if decoded_token.get("type") != expected_type:
        raise JWTError("Tipo de token inválido")
    return decoded_token

def create_telegram_token(user_id: int) -> str:
    expires_at = int(time.time()) + TELEGRAM_TOKEN_TTL

    # Payload:
    # 1 byte  -> version
    # 8 bytes -> user_id
    # 8 bytes -> expiration
    payload = (bytes([TELEGRAM_TOKEN_VERSION]) + user_id.to_bytes(8, "big") + expires_at.to_bytes(8, "big"))

    # Sig HMAC-SHA256
    # 16 bytes = 128 bits of signature
    signature = hmac.new(
        _get_secret_key().encode(),
        payload,
        hashlib.sha256,
    ).digest()[:16]

    token_bytes = payload + signature

    # Base64 URL-safe remove final "="
    token = base64.urlsafe_b64encode(token_bytes).rstrip(b"=").decode()

    return token

def verify_telegram_token(token: str) -> int | None:
    try:
        # Recreate generation removed padding
        padding = "=" * (-len(token) % 4)
        token_bytes = base64.urlsafe_b64decode(token + padding)

        if len(token_bytes) != 33:
            return None

        version = token_bytes[0]
        user_id = int.from_bytes(token_bytes[1:9], "big")
        expires_at = int.from_bytes(token_bytes[9:17], "big")
        signature = token_bytes[17:33]

        if version != TELEGRAM_TOKEN_VERSION:
            return None

        # Verify expiration
        if time.time() > expires_at:
            return None

        # Splits payload from signature
        payload = token_bytes[:17]

        expected_signature = hmac.new(
            _get_secret_key().encode(),
            payload,
            hashlib.sha256,
        ).digest()[:16]

        # Verify signature
        if not hmac.compare_digest(signature, expected_signature):
            return None

        return user_id

    except (ValueError, TypeError):
        return None
