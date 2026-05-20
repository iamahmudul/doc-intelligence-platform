from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, documents
from app.db.session import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Intelligence Platform",
    description="Multi-agent AI platform for document QnA, summarization, and semantic search",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Document Intelligence Backend"}