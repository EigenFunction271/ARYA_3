from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from auth import get_current_user, get_current_admin_user
from models import User, Token
from utils import process_uploaded_file, query_chatbot
import os

app = FastAPI()

# Allow CORS for frontend communication
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), user: User = Depends(get_current_admin_user)):
    return process_uploaded_file(file)

@app.post("/chat/")
async def chat(query: str, user: User = Depends(get_current_user)):
    return query_chatbot(query)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return get_current_user(form_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)