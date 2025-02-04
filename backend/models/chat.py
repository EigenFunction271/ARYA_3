from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    content: str
    timestamp: datetime
    role: str  # 'user' or 'assistant'
    
class ChatSession(BaseModel):
    session_id: str
    user_id: str
    messages: List[Message]
    created_at: datetime
    last_updated: datetime
    document_id: Optional[str] = None  # Reference to the document being queried
    
class ChatHistory(BaseModel):
    sessions: List[ChatSession] 