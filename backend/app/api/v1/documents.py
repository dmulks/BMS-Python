from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.document import MemberDocument
from app.schemas.document import DocumentResponse, DocumentWithUser

router = APIRouter(prefix="/documents", tags=["Documents"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.path.join("uploads", "member_documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document for the current user."""

    # Create user-specific directory
    user_dir = os.path.join(UPLOAD_DIR, str(current_user.user_id))
    os.makedirs(user_dir, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(user_dir, safe_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Get file size
    file_size = os.path.getsize(file_path)

    # Create database record
    db_document = MemberDocument(
        user_id=current_user.user_id,
        document_name=file.filename,
        document_type=document_type,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        description=description
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


@router.get("/my-documents", response_model=List[DocumentResponse])
def get_my_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user."""
    documents = db.query(MemberDocument).filter(
        MemberDocument.user_id == current_user.user_id
    ).order_by(MemberDocument.uploaded_at.desc()).all()

    return documents


@router.get("/all", response_model=List[DocumentWithUser])
def get_all_documents(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get all documents from all users (admin only)."""
    documents = db.query(
        MemberDocument,
        User.first_name,
        User.last_name,
        User.email
    ).join(User).order_by(MemberDocument.uploaded_at.desc()).all()

    result = []
    for doc, first_name, last_name, email in documents:
        doc_dict = {
            "document_id": doc.document_id,
            "user_id": doc.user_id,
            "document_name": doc.document_name,
            "document_type": doc.document_type,
            "file_path": doc.file_path,
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
            "description": doc.description,
            "uploaded_at": doc.uploaded_at,
            "updated_at": doc.updated_at,
            "user_first_name": first_name,
            "user_last_name": last_name,
            "user_email": email
        }
        result.append(doc_dict)

    return result


@router.get("/user/{user_id}", response_model=List[DocumentResponse])
def get_user_documents(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get all documents for a specific user (admin only)."""
    # Verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    documents = db.query(MemberDocument).filter(
        MemberDocument.user_id == user_id
    ).order_by(MemberDocument.uploaded_at.desc()).all()

    return documents


@router.get("/download/{document_id}")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a document."""
    document = db.query(MemberDocument).filter(
        MemberDocument.document_id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check permissions: user can only download their own documents, or admin can download any
    if document.user_id != current_user.user_id and current_user.user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to download this document"
        )

    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )

    return FileResponse(
        path=document.file_path,
        filename=document.document_name,
        media_type=document.mime_type or "application/octet-stream"
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document."""
    document = db.query(MemberDocument).filter(
        MemberDocument.document_id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check permissions: user can only delete their own documents, or admin can delete any
    if document.user_id != current_user.user_id and current_user.user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this document"
        )

    # Delete file from filesystem
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        print(f"Warning: Failed to delete file: {str(e)}")

    # Delete database record
    db.delete(document)
    db.commit()

    return None
