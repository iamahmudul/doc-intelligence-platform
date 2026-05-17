from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User

client = TestClient(app)

TEST_EMAIL = "testuser@example.com"

def cleanup_test_user():
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == TEST_EMAIL).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()

def test_register_user():
    cleanup_test_user()
    response = client.post("/api/v1/auth/register", json={
        "email": TEST_EMAIL,
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == TEST_EMAIL
    assert data["first_name"] == "Test"
    assert "hashed_password" not in data

def test_login_user():
    # First, register a user to ensure we have a valid user to log in with
    response = client.post("/api/v1/auth/login", json={
        "email": TEST_EMAIL,
        "password": "testpassword"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_wrong_password():
    response = client.post("/api/v1/auth/login", json={
        "email": TEST_EMAIL,
        "password": "wrongpassword"
    })

    assert response.status_code == 401
