from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.session import Base

class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=False)
    storage_key = Column(String, nullable=False, unique=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="documents")
