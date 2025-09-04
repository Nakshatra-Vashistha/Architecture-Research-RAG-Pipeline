"""
Script to initialize the database from JSONL files
Run this once to populate your ChromaDB from JSONL files
"""
from src.database import ResearchPaperDatabase
from src.config import config
import os

def setup_database():
    """Initialize database from JSONL files"""
    print("Initializing Research Paper Database...")
    
    # Create database instance
    db = ResearchPaperDatabase()
    
    # Check if JSONL files exist
    existing_files = []
    for file_path in config.JSONL_FILES:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"Found: {file_path}")
        else:
            print(f"Missing: {file_path}")
    
    if not existing_files:
        print("No JSONL files found. Please place your data files in the ./data/ directory")
        return
    
    # Add documents to database
    print(f"Processing {len(existing_files)} files...")
    db.add_documents_from_jsonl(existing_files)
    
    # Get stats
    stats = db.get_collection_stats()
    print(f"Database setup complete: {stats}")

if __name__ == "__main__":
    setup_database()
