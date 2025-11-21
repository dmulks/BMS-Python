from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MemberDocument(Base):
    """Model for storing member-uploaded documents."""
    __tablename__ = "member_documents"

    document_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=True)  # e.g., 'ID', 'Proof of Address', 'Other'
    file_path = Column(String(500), nullable=False)  # Path to stored file
    file_size = Column(Integer, nullable=True)  # Size in bytes
    mime_type = Column(String(100), nullable=True)  # e.g., 'application/pdf', 'image/jpeg'
    description = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<MemberDocument {self.document_name} (User: {self.user_id})>"