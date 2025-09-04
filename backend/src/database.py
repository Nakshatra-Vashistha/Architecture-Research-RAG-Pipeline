import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
import shutil
from typing import List, Dict, Any
import json
from backend.src.config import config

class ResearchPaperDatabase:
    def __init__(self):
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        print(f"Embedding model loaded with dimension: {self.embedding_model.get_sentence_embedding_dimension()}")
        
        # Clean up any existing database files first
        self._cleanup_old_database()
        
        # ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=config.PERSIST_DIRECTORY,
            settings=Settings(allow_reset=True)
        )
        
        self.collection = self._get_or_create_collection()
    
    def _cleanup_old_database(self):
        """Remove old database files that cause schema conflicts"""
        db_path = config.PERSIST_DIRECTORY
        if os.path.exists(db_path):
            print(f"🧹 Cleaning up old database files in {db_path}...")
            try:
                # Remove specific problematic files
                files_to_remove = [
                    "chroma.sqlite3",
                    "chroma.sqlite3-wal", 
                    "chroma.sqlite3-shm",
                    "index",
                    "index_metadata.pkl"
                ]
                
                for file_name in files_to_remove:
                    file_path = os.path.join(db_path, file_name)
                    if os.path.exists(file_path):
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            print(f"✅ Removed file: {file_name}")
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            print(f"✅ Removed directory: {file_name}")
                
                # If directory is empty after cleanup, remove it
                if not os.listdir(db_path):
                    shutil.rmtree(db_path)
                    os.makedirs(db_path, exist_ok=True)
                    print("✅ Completely reset database directory")
                    
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")
                # Continue anyway - maybe some files are locked
        else:
            os.makedirs(db_path, exist_ok=True)
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one with robust error handling"""
        try:
            # First try to get existing collection
            collection = self.client.get_collection(
                name=config.COLLECTION_NAME,
                embedding_function=self._get_embedding_function()
            )
            print(f"✅ Loaded existing collection: {config.COLLECTION_NAME}")
            return collection
            
        except Exception as e:
            print(f"⚠️ Could not load collection (will create new): {e}")
            
            # Try to delete any existing collection first
            try:
                self.client.delete_collection(config.COLLECTION_NAME)
                print(f"✅ Deleted old collection: {config.COLLECTION_NAME}")
            except:
                print("ℹ️ No existing collection to delete")
            
            # Create brand new collection
            collection = self.client.create_collection(
                name=config.COLLECTION_NAME,
                embedding_function=self._get_embedding_function(),
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✅ Created new collection: {config.COLLECTION_NAME}")
            return collection
    
    def _get_embedding_function(self):
        """Custom embedding function using SentenceTransformers with correct signature"""
        class SentenceTransformerEmbeddingFunction:
            def __init__(self, model):
                self.model = model
            
            def __call__(self, input: List[str]) -> List[List[float]]:
                """Correct signature for ChromaDB 0.4.x"""
                embeddings = self.model.encode(input)
                return embeddings.tolist()
        
        return SentenceTransformerEmbeddingFunction(self.embedding_model)
    
    def query_documents(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Query documents using semantic search"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            return results
        except Exception as e:
            print(f"❌ Query failed: {e}")
            # Return empty results in the expected format
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    
    def add_documents_from_jsonl(self, jsonl_files: List[str]):
        """Add documents from JSONL files to the database"""
        documents = []
        metadatas = []
        ids = []
        
        for file_path in jsonl_files:
            if not os.path.exists(file_path):
                print(f"⚠️ File not found: {file_path}")
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    try:
                        data = json.loads(line.strip())
                        documents.append(data.get('text', ''))
                        metadatas.append(data.get('metadata', {}))
                        ids.append(f"{os.path.basename(file_path)}_{i}")
                    except json.JSONDecodeError:
                        print(f"⚠️ Invalid JSON in {file_path}, line {i+1}")
        
        if documents:
            try:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"✅ Added {len(documents)} documents to collection")
            except Exception as e:
                print(f"❌ Failed to add documents: {e}")
        else:
            print("⚠️ No documents to add")
    
    def persist(self):
        """Persist the database"""
        print("💾 Database persistence handled automatically")