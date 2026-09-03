import os
import uvicorn
import sqlite3
from fastapi import FastAPI
from dotenv import load_dotenv
from routes.auth_routes import auth_router

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()
app.include_router(auth_router)

#Cria o banco de dados
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chatID(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.post("/string")
def save_string(chat_id: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chatID (chat_id) VALUES (?)",
        (chat_id,)
    )

    conn.commit()
    conn.close()

    return {
        "message": "Chat ID salvo com sucesso!",
        "chatID": chat_id
    }
@app.get("/strings")
def get_strings():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, chat_id FROM chatID")
    strings = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "chat_id": row[1]
        }
        for row in strings
    ]

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
