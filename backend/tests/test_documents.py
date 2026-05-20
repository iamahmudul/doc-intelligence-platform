from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.document import Document
import io

client = TestClient(app)

TEST_EMAIL = "doctest@example.com"
TEST_PASSWORD = "securepassword123"

def get_auth_token():
    db: SessionLocal = SessionLocal()
    db.query(User).filter(User.email == TEST_EMAIL).delete()
    db.commit()
    db.close()

    # Register the user
    client.post("/api/v1/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "first_name": "Doc",
        "last_name": "Tester"
    })

    response = client.post("/api/v1/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })

    return response.json()["access_token"]

def make_pdf_bytes():
    token = get_auth_token()
    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 test pdf content"), "application/pdf")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["status"] == "uploaded"

def test_upload_non_pdf_rejected():
    token = get_auth_token()
    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.txt", io.BytesIO(b"Just some text content"), "text/plain")}
    )
    assert response.status_code == 400

def test_list_documents():
    token = get_auth_token()
    #upload a document to ensure we have at least one document to list
    # client.post(
    #     "/api/v1/documents/upload",
    #     headers={"Authorization": f"Bearer {token}"},
    #     files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 test pdf content"), "application/pdf")}
    # )

    response = client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "documents" in response.json()

def test_upload_requires_authentication():
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 test pdf content"), "application/pdf")}
    )
    assert response.status_code == 403

