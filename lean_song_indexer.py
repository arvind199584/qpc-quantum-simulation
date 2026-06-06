import os
import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np

# --- CONFIGURATION ---
DB_CONFIG = {
    "dbname": "bollywood_db",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

# Load the multilingual model (Hindi, Urdu, English support)
# This model is small and fast (~420MB)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def init_lean_db():
    """Create the table for Names, Paths, and Vectors (No Blobs)."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    # Ensure pgvector extension is available
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS song_index (
            id SERIAL PRIMARY KEY,
            file_name TEXT,
            file_path TEXT UNIQUE, -- The 'Address' on your hard drive
            semantic_vec VECTOR(384), -- The NLP 'Meaning' map
            tags JSONB,              -- Inferred categories (e.g. {"Haldi": 0.9})
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_path ON song_index(file_path);
    """)
    conn.commit()
    cur.close()
    conn.close()

def process_bollywood_library(root_folder):
    """Scan files and save only Name, Address, and Meaning to Postgres."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    video_exts = ('.mp4', '.mov', '.mkv', '.avi')
    
    print(f"Indexing Library: {root_folder}")

    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(video_exts):
                full_path = os.path.abspath(os.path.join(root, file))
                
                # Check if we already have this address
                cur.execute("SELECT id FROM song_index WHERE file_path = %s", (full_path,))
                if cur.fetchone():
                    continue

                # 1. Clean the name for NLP (remove extension, underscores, etc.)
                clean_name = file.replace('_', ' ').split('.')[0]
                
                # 2. Generate the 'Meaning' Vector
                # This turns "Mehndi Laga Ke Rakhna" into 384 numbers
                vector = model.encode(clean_name).tolist()

                # 3. Store in Postgres (Lean: No video data, just metadata)
                try:
                    cur.execute("""
                        INSERT INTO song_index (file_name, file_path, semantic_vec)
                        VALUES (%s, %s, %s)
                    """, (file, full_path, vector))
                    conn.commit()
                    print(f"Indexed: {file}")
                except Exception as e:
                    conn.rollback()
                    print(f"Error indexing {file}: {e}")

    cur.close()
    conn.close()
    print("Indexing Complete!")

if __name__ == "__main__":
    # 1. init_lean_db()
    # 2. process_bollywood_library("F:/Bollywood_Collection")
    pass
