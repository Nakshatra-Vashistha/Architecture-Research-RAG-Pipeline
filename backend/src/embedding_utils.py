import os
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self, model_name="multi-qa-MiniLM-L6-cos-v1"):
        print(f"Loading embedding model: {model_name}")
        
        # Use environment variable or fallback to /tmp/.cache
        cache_dir = os.getenv('TRANSFORMERS_CACHE', '/tmp/.cache')
        print(f"Using cache directory: {cache_dir}")
        
        # Create the cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Embedding model loaded with dimension: {self.dimension}")
    
    def embed_text(self, text):
        """Convert text to embedding vector"""
        if isinstance(text, str):
            return self.model.encode(text).tolist()
        elif isinstance(text, list):
            return self.model.encode(text).tolist()
        else:
            raise ValueError("Input must be string or list of strings")
    
    def embed_query(self, query):
        """Embed a single query"""
        return self.embed_text(query)
    
    def embed_documents(self, documents):
        """Embed multiple documents"""
        return self.embed_text(documents)