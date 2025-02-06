from supabase import create_client
import os
import magic
from models.document import Document, FileType
from typing import List, Tuple
import uuid
from pypdf import PdfReader
from io import BytesIO

class DocumentManager:
    ALLOWED_MIMETYPES = {
        'text/plain': FileType.TEXT,
        'application/pdf': FileType.PDF,
        'text/markdown': FileType.MARKDOWN
    }

    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    def _detect_file_type(self, content: bytes) -> FileType:
        mime = magic.from_buffer(content, mime=True)
        if mime not in self.ALLOWED_MIMETYPES:
            raise ValueError(f"Unsupported file type: {mime}")
        return self.ALLOWED_MIMETYPES[mime]
    
    def _extract_text(self, content: bytes, file_type: FileType) -> Tuple[str, dict]:
        metadata = {}
        
        if file_type == FileType.TEXT:
            return content.decode('utf-8'), metadata
            
        elif file_type == FileType.PDF:
            pdf = PdfReader(BytesIO(content))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            metadata['page_count'] = len(pdf.pages)
            return text, metadata
            
        elif file_type == FileType.MARKDOWN:
            return content.decode('utf-8'), metadata
            
        raise ValueError(f"Unsupported file type: {file_type}")

    async def store_document(self, file_content: bytes, filename: str, uploader_email: str) -> Tuple[Document, str]:
        # Generate unique ID
        doc_id = str(uuid.uuid4())
        
        # Detect file type and extract text
        file_type = self._detect_file_type(file_content)
        text_content, metadata = self._extract_text(file_content, file_type)
        
        # Store original file in Supabase Storage
        storage_path = f"documents/{doc_id}/{filename}"
        self.supabase.storage.from_("documents").upload(
            storage_path,
            file_content
        )
        
        # Create document record
        document = Document(
            id=doc_id,
            filename=filename,
            uploader_email=uploader_email,
            pinecone_namespace=doc_id,
            file_type=file_type,
            file_size=len(file_content),
            **metadata
        )
        
        # Store metadata in Supabase
        self.supabase.table("documents").insert(document.dict()).execute()
        
        return document, text_content

    def get_user_documents(self, email: str) -> List[Document]:
        response = self.supabase.table("documents")\
            .select("*")\
            .eq("uploader_email", email)\
            .eq("status", "active")\
            .execute()
        return [Document(**doc) for doc in response.data] 