import os
import zipfile
import gdown
import shutil
from huggingface_hub import snapshot_download

# 🔹 Replace with your real HF repo ID if using HF dataset
HF_REPO_ID = "nakshVashisth/chroma-db"

def get_db_dir():
    """Return a writable dir for ChromaDB."""
    # For HF Spaces, use /tmp for writable storage
    return "/tmp/chroma_db"

def cleanup_before_download():
    """Clean up before downloading new database"""
    db_dir = get_db_dir()
    if os.path.exists(db_dir):
        print("🧹 Cleaning up before download...")
        try:
            shutil.rmtree(db_dir)
            os.makedirs(db_dir, exist_ok=True)
            print("✅ Cleaned up directory for fresh download")
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")

def load_from_hf():
    """Try to restore DB from HF dataset repo cache."""
    try:
        local_dir = snapshot_download(HF_REPO_ID, repo_type="dataset")
        db_dir = os.path.join(local_dir, "chroma_db")
        if os.path.exists(db_dir) and os.listdir(db_dir):
            print(f"✅ Loaded ChromaDB from HF Hub at {db_dir}")
            return db_dir
    except Exception as e:
        print(f"⚠️ Could not load from HF Hub: {e}")
    return None

def download_from_drive():
    """Download DB from Google Drive and extract."""
    db_dir = get_db_dir()
    
    # Check if DB already exists and is not empty
    if os.path.exists(db_dir) and os.listdir(db_dir):
        print(f"✅ DB already exists at {db_dir}")
        return db_dir

    os.makedirs(db_dir, exist_ok=True)

    # Create cache directory for gdown
    cache_dir = "/tmp/.cache/gdown"
    os.makedirs(cache_dir, exist_ok=True)
    os.environ['GDOWN_CACHE_DIR'] = cache_dir

    # Replace with your actual Google Drive file ID
    file_id = "1vgBY8YSsiHMUZrl6obGilJQLYuljS4bJ"
    url = f"https://drive.google.com/uc?id={file_id}"
    output = os.path.join(os.path.dirname(db_dir), "chroma_db.zip")

    print(f"⬇️ Downloading ChromaDB from Google Drive...")
    
    try:
        # Download with explicit cookie file path
        gdown.download(url, output, quiet=False, use_cookies=False)
        
        print("📂 Extracting database...")
        with zipfile.ZipFile(output, "r") as zip_ref:
            zip_ref.extractall(os.path.dirname(db_dir))
        
        # Clean up zip file
        if os.path.exists(output):
            os.remove(output)
            
        print(f"✅ Extracted ChromaDB to {db_dir}")
        
        # Verify extraction was successful
        if os.path.exists(db_dir) and os.listdir(db_dir):
            print(f"✅ ChromaDB verification successful - {len(os.listdir(db_dir))} items found")
            return db_dir
        else:
            print("❌ ChromaDB extraction failed - directory is empty")
            return None
            
    except Exception as e:
        print(f"❌ Failed to download from Google Drive: {e}")
        # Clean up partial downloads
        if os.path.exists(output):
            os.remove(output)
        return None

def download_and_extract_db():
    """Ensure DB is available locally."""
    # Clean up any existing files first to avoid conflicts
    cleanup_before_download()
    
    db_dir = get_db_dir()
    
    print(f"🔍 Checking for ChromaDB at {db_dir}...")
    
    # Check if DB already exists and is not empty
    if os.path.exists(db_dir) and os.listdir(db_dir):
        print(f"✅ ChromaDB already exists at {db_dir}")
        return db_dir

    # Try HF Hub first (if you have it set up)
    print("🔄 Trying to load from Hugging Face Hub...")
    hf_db_dir = load_from_hf()
    if hf_db_dir:
        # Copy from HF cache to our target directory
        try:
            shutil.copytree(hf_db_dir, db_dir)
            print(f"✅ Copied ChromaDB from HF to {db_dir}")
            return db_dir
        except Exception as e:
            print(f"⚠️ Failed to copy from HF: {e}")

    # Fallback to Google Drive download
    print("🔄 Downloading from Google Drive...")
    result = download_from_drive()
    if result:
        return result
    
    # If all else fails, ensure the directory exists
    os.makedirs(db_dir, exist_ok=True)
    print("⚠️ All download methods failed, returning empty directory")
    return db_dir

# For testing
if __name__ == "__main__":
    db_path = download_and_extract_db()
    if db_path and os.path.exists(db_path) and os.listdir(db_path):
        print(f"✅ Success! ChromaDB ready at: {db_path}")
        print(f"📁 Contains {len(os.listdir(db_path))} items")
    else:
        print("❌ ChromaDB download failed or directory is empty")