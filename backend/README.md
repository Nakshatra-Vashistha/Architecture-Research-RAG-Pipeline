# Architecture RAG Backend

This FastAPI backend connects your existing RAG pipeline to the React frontend.

## Setup Instructions

### 1. Install Dependencies
\`\`\`bash
cd backend
pip install -r requirements.txt
\`\`\`

### 2. Setup Vector Database
Before running the backend, you need to set up your 500MB vector database:

1. **Copy your JSONL files**: Update the paths in `src/config.py` to point to your actual JSONL files:
   \`\`\`python
   JSONL_FILES = [
       "path/to/your/building_codes_chunks.jsonl",
       "path/to/your/case_studies_chunks.jsonl",
       "path/to/your/material_guide_chunks.jsonl",
       "path/to/your/misc_chunks.jsonl"
   ]
   \`\`\`

2. **Initialize the database** (one-time setup):
   \`\`\`bash
   python -c "
   import sys
   sys.path.append('src')
   from src.rag_pipeline import RAGPipeline
   from src.config import config
   rag = RAGPipeline()
   rag.initialize_database(config.JSONL_FILES)
   "
   \`\`\`

   This will create a `chroma_db` folder with your vector database.

### 3. Start Ollama
Make sure Ollama is running with your model:
\`\`\`bash
ollama serve
ollama pull llama2  # or your preferred model
\`\`\`

### 4. Run the Backend
\`\`\`bash
python main.py
\`\`\`

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /api/query` - Single query mode
- `POST /api/interactive` - Interactive conversation mode
- `GET /api/stats` - Database statistics
- `POST /api/initialize` - Initialize database (if needed)

## Frontend Connection

The React frontend is configured to connect to `http://localhost:8000`. Make sure both servers are running:

1. Backend: `python backend/main.py` (port 8000)
2. Frontend: `npm run dev` (port 3000)
