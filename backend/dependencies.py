from models import db
from sqlalchemy.orm import Session, sessionmaker
from models import User
from core.security import verify_token
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

SessionLocal = sessionmaker(bind=db, autoflush=False, autocommit=False)

def get_session():
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_authenticated_user(token: str = Depends(oauth2_schema), session: Session = Depends(get_session)):
    try:
        decoded_token = verify_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso negado. Verifique a validade do token")
    user = session.query(User).filter(User.id==int(decoded_token.get('sub'))).first()

    if not user:
        raise HTTPException(status_code=401, detail="Acesso Inválido")

    return user
