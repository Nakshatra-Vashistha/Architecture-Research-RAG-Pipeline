import os
from pathlib import Path


class Config:
    # Embedding model
    EMBEDDING_MODEL = "multi-qa-MiniLM-L6-cos-v1"

    # Base paths - updated for your new structure
    BASE_DIR = Path(__file__).resolve().parent.parent

    # ChromaDB path - use /tmp for HF Spaces (writable)
    PERSIST_DIRECTORY = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db")

    # ChromaDB settings
    COLLECTION_NAME = "architecture_research_papers"

    # JSONL sources (only if you rebuild) - update paths
    JSONL_FILES = [
        str(BASE_DIR / "data" / "building_codes_chunks.jsonl"),
        str(BASE_DIR / "data" / "case_studies_chunks.jsonl"),
        str(BASE_DIR / "data" / "material_guide_chunks.jsonl"),
        str(BASE_DIR / "data" / "misc_chunks.jsonl"),
    ]

    # LLM settings - updated for HF Spaces compatibility
    OLLAMA_MODEL = os.getenv("LLM_MODEL", "llama2")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # HF Inference API settings
    HF_API_MODEL = os.getenv("HF_API_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")

    # RAG settings
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # Environment detection
    IS_HF_SPACES = os.getenv("SPACE_ID") is not None
    USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"


config = Config()