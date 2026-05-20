from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.document import DocumentStatus

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    status: DocumentStatus
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int

