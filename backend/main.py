import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import Base, db
from routes.auth_routes import auth_router
from routes.chat_routes import chat_router

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

Base.metadata.create_all(bind=db)

app = FastAPI()
app.include_router(auth_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
