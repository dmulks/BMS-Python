from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentUpload(BaseModel):
    """Schema for uploading a document."""
    document_type: Optional[str] = None
    description: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document response."""
    document_id: int
    user_id: int
    document_name: str
    document_type: Optional[str]
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    description: Optional[str]
    uploaded_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentWithUser(DocumentResponse):
    """Schema for document with user information (for admin view)."""
    user_first_name: str
    user_last_name: str
    user_email: str

    class Config:
        from_attributes = True