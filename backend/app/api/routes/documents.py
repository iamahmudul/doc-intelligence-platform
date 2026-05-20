from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.storage import upload_file, get_presigned_url, delete_file
from app.models.document import Document, DocumentStatus
from app.models.schemas import DocumentResponse, DocumentListResponse
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_MIME_TYPES = {"application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    #validate mime type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    #validate file size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10 MB limit"
            )
        
    #validate pdf magic bytes
    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file"
        )
    
    #generate unique storage key
    storage_key = f"users/{current_user.id}/documents/{uuid.uuid4()}.pdf"

    try:
        upload_file(file_bytes, storage_key, file.content_type)
    except Exception as e:
        logger.error(f"Storage upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )
    print(f"========5========")
    
    #save document metadata to database
    document = Document(
        user_id=current_user.id,
        storage_key=storage_key,
        filename=storage_key.split("/")[-1],
        original_filename=file.filename,
        file_size=len(file_bytes),
        mime_type=file.content_type,
        status=DocumentStatus.UPLOADED
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

@router.get("/", response_model=DocumentListResponse)
def list_documents(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return DocumentListResponse(documents=documents, total=len(documents))

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    try:
        delete_file(document.storage_key)
    except Exception as e:
        logger.error(f"Storage deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file from storage"
        )

    db.delete(document)
    db.commit()