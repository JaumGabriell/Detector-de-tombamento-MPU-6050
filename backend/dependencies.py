from models import db
from sqlalchemy.orm import Session, sessionmaker

SessionLocal = sessionmaker(bind=db, autoflush=False, autocommit=False)

def get_session():
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
