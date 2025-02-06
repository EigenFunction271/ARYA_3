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
from models.user import UserCreate, UserRole
from user_manager import UserManager
from document_manager import DocumentManager
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone

app = FastAPI()
session_manager = SessionManager()

# Create embeddings and store in Pinecone
llm_provider_value = os.getenv("LLM_PROVIDER", "mistral").split('#')[0].strip()
current_provider = LLMProvider(llm_provider_value)
embeddings = get_embeddings(current_provider)

# Initialize user manager
user_manager = UserManager()

# Initialize document manager
document_manager = DocumentManager()

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
    current_user: User = Depends(get_current_user)
):
    # Read file content
    content = await file.read()
    
    try:
        # Store document and get metadata
        document, text_content = await document_manager.store_document(
            content,
            file.filename,
            current_user.email
        )
        
        # Process for RAG
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_text(text_content)
        
        # Store in Pinecone with document namespace
        embeddings = get_embeddings(current_provider)
        Pinecone.from_texts(
            texts,
            embeddings,
            index_name=os.getenv("PINECONE_INDEX_NAME"),
            namespace=document.id
        )
        
        return {
            "message": "File uploaded and processed successfully",
            "document_id": document.id,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "page_count": document.page_count
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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

@app.post("/register")
async def register_user(user: UserCreate):
    """Register a new user"""
    try:
        db_user = user_manager.create_user(user)
        return {"message": "User created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/users/{username}/role")
async def set_user_role(
    username: str,
    role: UserRole,
    current_user: User = Depends(get_current_admin_user)
):
    """Set user role (admin only)"""
    db_user = user_manager.set_user_role(username, role)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"Role updated to {role}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)