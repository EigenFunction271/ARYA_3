from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from typing import List
import os

# Local imports
from auth import (
    get_current_user, 
    get_current_admin_user, 
    authenticate_user, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import User
from models.chat import ChatSession, Message
from utils import process_uploaded_file, query_chatbot
from session_manager import SessionManager
from llm_config import LLMProvider, get_embeddings

app = FastAPI()
session_manager = SessionManager()

# Create embeddings and store in Pinecone
llm_provider_value = os.getenv("LLM_PROVIDER", "mistral").split('#')[0].strip()
current_provider = LLMProvider(llm_provider_value)
embeddings = get_embeddings(current_provider)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...), 
    user: User = Depends(get_current_admin_user)
):
    """Upload and process a document (admin only)"""
    return process_uploaded_file(file)

@app.post("/chat/session")
async def create_chat_session(
    document_id: str = None,
    user: User = Depends(get_current_user)
) -> ChatSession:
    """Create a new chat session"""
    return session_manager.create_session(user["username"], document_id)

@app.get("/chat/sessions")
async def get_user_sessions(
    user: User = Depends(get_current_user)
) -> List[ChatSession]:
    """Get all chat sessions for the current user"""
    return session_manager.get_user_sessions(user["username"])

@app.delete("/chat/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    user: User = Depends(get_current_user)
) -> dict:
    """Delete a chat session"""
    if session_manager.delete_session(session_id, user["username"]):
        return {"message": "Session deleted successfully"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/chat/{session_id}")
async def chat(
    session_id: str,
    query: str,
    user: User = Depends(get_current_user)
):
    """Send a message in a specific chat session"""
    session = session_manager.get_session(session_id)
    if not session or session.user_id != user["username"]:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Add user message to history
    session_manager.add_message(session_id, query, "user")
    
    try:
        # Get chatbot response using the configured LLM provider
        response = query_chatbot(query)
        
        # Add assistant response to history
        session_manager.add_message(session_id, response["response"], "assistant")
        
        return response
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        session_manager.add_message(session_id, error_msg, "system")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/chat/{session_id}/history")
async def get_chat_history(
    session_id: str,
    user: User = Depends(get_current_user)
) -> List[Message]:
    """Get chat history for a specific session"""
    session = session_manager.get_session(session_id)
    if not session or session.user_id != user["username"]:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.messages

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Optional: Add endpoint to change LLM provider
@app.post("/config/llm-provider")
async def set_llm_provider(
    provider: LLMProvider,
    user: User = Depends(get_current_admin_user)
):
    """Change the LLM provider (admin only)"""
    global current_provider
    current_provider = provider
    return {"message": f"LLM provider changed to {provider}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)