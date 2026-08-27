import os
import uvicorn
from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
from routes.auth_routes import auth_router

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
if url and key:
    supabase: Client = create_client(url, key)

# comando pra rodar: uvicorn main:app --reload
app = FastAPI()

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)