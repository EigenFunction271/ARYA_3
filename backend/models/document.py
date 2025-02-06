from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class FileType(str, Enum):
    TEXT = "text"
    PDF = "pdf"
    MARKDOWN = "markdown"

class Document(BaseModel):
    id: str
    filename: str
    uploader_email: str
    pinecone_namespace: Optional[str] = None
    upload_date: datetime = datetime.utcnow()
    file_type: FileType
    status: str = "active"
    page_count: Optional[int] = None
    file_size: Optional[int] = None 