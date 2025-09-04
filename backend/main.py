from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

from backend.download_db import download_and_extract_db

# ✅ Download and extract DB if needed
download_and_extract_db()

# ✅ Add backend/src to Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from backend.src.rag_pipeline import RAGPipeline

# ✅ FastAPI app
app = FastAPI(title="Architecture RAG API", version="1.0.0")

# ✅ Enable CORS for external frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🚨 Change to ["https://your-frontend.vercel.app"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Initialize RAG pipeline
rag_pipeline = RAGPipeline()

# Request model
class Query(BaseModel):
    question: str
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    context: List[str]
    query: str

@app.get("/")
async def root():
    """API root endpoint"""
    return JSONResponse(
        content={
            "message": "RAG API is running 🚀",
            "status": "backend_online",
            "endpoints": {
                "api": "/ask",
                "health": "/health",
                "docs": "/docs"
            }
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "backend": True,
        "chroma_db_exists": os.path.exists("/tmp/chroma_db") and os.listdir("/tmp/chroma_db"),
        "endpoints": {
            "api": "/ask",
            "health": "/health",
            "docs": "/docs"
        }
    }
    
    if not health_status["chroma_db_exists"]:
        health_status["status"] = "degraded"
        health_status["warning"] = "ChromaDB not found - check download logs"
    
    return health_status

@app.post("/ask", response_model=QueryResponse)
async def ask(query: Query):
    """Main RAG query endpoint"""
    try:
        result = rag_pipeline.query(query.question, n_results=query.top_k)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
