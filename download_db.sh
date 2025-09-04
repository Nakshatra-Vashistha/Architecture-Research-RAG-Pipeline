#!/bin/bash

echo "🔍 Checking if ChromaDB needs to be downloaded..."

# Create cache directory for gdown
mkdir -p /tmp/.cache/gdown

# Check if chroma_db directory exists and is not empty
if [ -d "/tmp/chroma_db" ] && [ "$(ls -A /tmp/chroma_db)" ]; then
    echo "✅ ChromaDB already exists at /tmp/chroma_db"
else
    echo "📥 ChromaDB not found. Downloading..."
    
    # Create the directory
    mkdir -p /tmp/chroma_db
    
    # Run your Python download script
    python -c "
import sys
sys.path.append('/app')
from backend.download_db import download_and_extract_db
try:
    result = download_and_extract_db()
    if result and os.path.exists(result) and os.listdir(result):
        print('✅ ChromaDB download completed successfully')
    else:
        print('⚠️ ChromaDB directory exists but may be empty')
except Exception as e:
    print(f'❌ ChromaDB download failed: {e}')
    # Don't exit - let the app start anyway
    "
    
    # Verify download was successful
    if [ -d "/tmp/chroma_db" ] && [ "$(ls -A /tmp/chroma_db)" ]; then
        echo "✅ ChromaDB downloaded successfully to /tmp/chroma_db"
    else
        echo "⚠️ ChromaDB directory exists but may be empty - continuing anyway"
    fi
fi

echo "🚀 Starting application..."
exec "$@"