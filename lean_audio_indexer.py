import os
import hashlib
import psycopg2
from sentence_transformers import SentenceTransformer
from pathlib import Path

# --- UPDATED CONFIGURATION ---
DB_CONFIG = {
    "dbname": "Daredevil Songs",
    "user": "postgres",
    "password": "daredevil",
    "host": "localhost",
    "port": "5432"
}

# Load multilingual NLP model (will download on first run ~420MB)
print("Loading NLP Model...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_file_hash(file_path):
    """Generate a quick hash to detect exact duplicates (first 1MB + size)."""
    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            chunk = f.read(1024 * 1024)
            return hashlib.md5(chunk + str(file_size).encode()).hexdigest()
    except:
        return None

def index_audio_library(root_folder):
    """Process 200k MP3s: Detect duplicates and map meanings."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    audio_exts = ('.mp3', '.wav', '.m4a', '.flac')
    
    print(f"Scanning Audio Library: {root_folder}")

    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(audio_exts):
                full_path = os.path.abspath(os.path.join(root, file))
                
                # Check if path exists in DB
                cur.execute("SELECT id FROM audio_index WHERE file_path = %s", (full_path,))
                if cur.fetchone():
                    continue

                f_hash = get_file_hash(full_path)
                
                # NLP Processing
                clean_name = Path(file).stem.replace('_', ' ').replace('-', ' ')
                vector = model.encode(clean_name).tolist()

                try:
                    cur.execute("""
                        INSERT INTO audio_index (file_name, file_path, file_hash, semantic_vec)
                        VALUES (%s, %s, %s, %s)
                    """, (file, full_path, f_hash, vector))
                    conn.commit()
                    print(f"Indexed: {file}")
                except Exception as e:
                    conn.rollback()
                    print(f"Error indexing {file}: {e}")

    cur.close()
    conn.close()
    print("All songs indexed in 'Daredevil Songs' database!")

if __name__ == "__main__":
    # Start the 200k scan
    index_audio_library(r"F:\songs")
