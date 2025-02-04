from datetime import datetime
import uuid
from typing import Dict, List, Optional
import json
import os
from models.chat import Message, ChatSession, ChatHistory

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.user_sessions: Dict[str, List[str]] = {}
        self._load_sessions()
    
    def create_session(self, user_id: str, document_id: Optional[str] = None) -> ChatSession:
        """Create a new chat session for a user"""
        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            messages=[],
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            document_id=document_id
        )
        self.sessions[session_id] = session
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)
        
        self._save_sessions()
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a specific chat session"""
        return self.sessions.get(session_id)
    
    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        """Get all chat sessions for a user"""
        session_ids = self.user_sessions.get(user_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]
    
    def add_message(self, session_id: str, content: str, role: str) -> Optional[Message]:
        """Add a message to a chat session"""
        if session_id not in self.sessions:
            return None
            
        message = Message(
            content=content,
            timestamp=datetime.utcnow(),
            role=role
        )
        
        self.sessions[session_id].messages.append(message)
        self.sessions[session_id].last_updated = datetime.utcnow()
        self._save_sessions()
        return message
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a chat session"""
        if session_id not in self.sessions or self.sessions[session_id].user_id != user_id:
            return False
        
        del self.sessions[session_id]
        if user_id in self.user_sessions:
            self.user_sessions[user_id].remove(session_id)
        self._save_sessions()
        return True
    
    def _save_sessions(self):
        """Save sessions to disk"""
        os.makedirs('data', exist_ok=True)
        with open('data/sessions.json', 'w') as f:
            json.dump({
                'sessions': {
                    sid: session.dict() 
                    for sid, session in self.sessions.items()
                },
                'user_sessions': self.user_sessions
            }, f, default=str)
    
    def _load_sessions(self):
        """Load sessions from disk"""
        try:
            with open('data/sessions.json', 'r') as f:
                data = json.load(f)
                self.sessions = {
                    sid: ChatSession(**session_data)
                    for sid, session_data in data['sessions'].items()
                }
                self.user_sessions = data['user_sessions']
        except (FileNotFoundError, json.JSONDecodeError):
            self.sessions = {}
            self.user_sessions = {} 