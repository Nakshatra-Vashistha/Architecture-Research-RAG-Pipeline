import requests
from typing import List, Dict, Any
import os
from backend.src.config import config
from .database import ResearchPaperDatabase


class RAGPipeline:
    def __init__(self):
        self.db = ResearchPaperDatabase()
        self.llm_api_url = os.getenv("LLM_API_URL", config.OLLAMA_BASE_URL)
        self.llm_model = os.getenv("LLM_MODEL", config.OLLAMA_MODEL)
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    
    def generate_response_ollama(self, query: str, context: List[str]) -> str:
        """Generate response using Ollama"""
        try:
            import ollama
            client = ollama.Client(host=self.llm_api_url)
            
            context_text = "\n\n".join([
                f"Reference {i+1}:\n{doc}" for i, doc in enumerate(context)
            ])
            
            system_prompt = """You are an expert in architecture research. Use the provided research paper excerpts to answer the user's question accurately and comprehensively. 

            Guidelines:
            1. Base your answer strictly on the provided context
            2. If the context doesn't contain relevant information, say so
            3. Cite specific references when possible
            4. Provide detailed, technical answers appropriate for architecture research
            5. Maintain academic tone and precision
            """
            
            user_prompt = f"""Based on the following research excerpts, answer this question: {query}

            Research Context:
            {context_text}

            Please provide a comprehensive answer citing relevant sections from the research papers."""

            response = client.chat(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return response['message']['content']
        
        except ImportError:
            return "Ollama not available. Please check your installation."
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_response_openai(self, query: str, context: List[str]) -> str:
        """Generate response using OpenAI-compatible API"""
        context_text = "\n\n".join([
            f"Reference {i+1}:\n{doc}" for i, doc in enumerate(context)
        ])
        
        system_prompt = """You are an expert in architecture research. Use the provided research paper excerpts to answer the user's question accurately and comprehensively. 

        Guidelines:
        1. Base your answer strictly on the provided context
        2. If the context doesn't contain relevant information, say so
        3. Cite specific references when possible
        4. Provide detailed, technical answers appropriate for architecture research
        5. Maintain academic tone and precision
        """
        
        user_prompt = f"""Based on the following research excerpts, answer this question: {query}

        Research Context:
        {context_text}

        Please provide a comprehensive answer citing relevant sections from the research papers."""

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}"
            }
            
            payload = {
                "model": self.llm_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{self.llm_api_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_response(self, query: str, context: List[str]) -> str:
        """Generate response using appropriate LLM backend"""
        if self.use_ollama:
            return self.generate_response_ollama(query, context)
        else:
            return self.generate_response_openai(query, context)
    
    def query(self, user_query: str, n_results: int = config.TOP_K_RESULTS) -> Dict[str, Any]:
        """Complete RAG pipeline: retrieve and generate"""
        
        # Step 1: Query the database
        print("Searching for relevant research papers...")
        results = self.db.query_documents(user_query, n_results)
        
        if not results or not results['documents']:
            return {
                "answer": "No relevant research papers found for your query.",
                "sources": [],
                "context": []
            }
        
        # Extract retrieved documents
        retrieved_docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0] if 'distances' in results else [0] * len(metadatas)
        
        # Step 2: Generate response
        print("Generating comprehensive answer...")
        answer = self.generate_response(user_query, retrieved_docs)
        
        # Prepare source information
        sources = []
        for i, (metadata, distance) in enumerate(zip(metadatas, distances)):
            source_info = {
                "source_id": i+1,
                "title": metadata.get('title', 'Unknown Title'),
                "authors": metadata.get('authors', []),
                "year": metadata.get('year', 'Unknown'),
                "confidence": f"{1 - distance:.3f}" if distance is not None else "N/A"
            }
            sources.append(source_info)
        
        return {
            "answer": answer,
            "sources": sources,
            "context": retrieved_docs,
            "query": user_query
        }
    
    def initialize_database(self, jsonl_files: List[str]):
        """Initialize the database with research papers"""
        print("Initializing database with research papers...")
        self.db.add_documents_from_jsonl(jsonl_files)
        self.db.persist()
        print("Database initialization complete!")