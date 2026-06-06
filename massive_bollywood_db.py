import os
import cv2
import numpy as np
import psycopg2
from pathlib import Path

# Database Connection Settings
DB_CONFIG = {
    "dbname": "bollywood_media",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

def init_db():
    """Initialize the PostgreSQL table for media assets."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id SERIAL PRIMARY KEY,
            file_name TEXT,
            file_path TEXT UNIQUE,
            category TEXT, -- 'Bollywood', 'Serial', 'Song'
            has_face BOOLEAN,
            is_action BOOLEAN,
            is_blurry BOOLEAN,
            duration_sec FLOAT,
            file_size_mb FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_category ON assets(category);
        CREATE INDEX IF NOT EXISTS idx_tags ON assets(has_face, is_action);
    """)
    conn.commit()
    cur.close()
    conn.close()

def scan_and_analyze(root_folder):
    """Scan folder and save analysis to Postgres."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    video_exts = ('.mp4', '.mov', '.mkv', '.avi')

    print(f"Starting massive scan of: {root_folder}")

    for root, dirs, files in os.walk(root_folder):
        # Infer category from folder name
        category = "Unknown"
        if "song" in root.lower(): category = "Song"
        elif "serial" in root.lower(): category = "Serial"
        elif "bollywood" in root.lower(): category = "Bollywood"

        for file in files:
            if file.lower().endswith(video_exts):
                full_path = os.path.join(root, file)
                
                # Skip if already in DB
                cur.execute("SELECT id FROM assets WHERE file_path = %s", (full_path,))
                if cur.fetchone():
                    continue

                print(f"Processing: {file}")
                
                # Basic File Info
                file_size = os.path.getsize(full_path) / (1024 * 1024)
                
                # AI Analysis
                cap = cv2.VideoCapture(full_path)
                has_face = False
                motion_total = 0
                blur_total = 0
                frames_sampled = 0
                
                if cap.isOpened():
                    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
                    # Sample 30 frames
                    for _ in range(30):
                        ret, frame = cap.read()
                        if not ret: break
                        
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        # Face check
                        if not has_face and frames_sampled % 10 == 0:
                            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                            if len(faces) > 0: has_face = True
                        
                        blur_total += cv2.Laplacian(gray, cv2.CV_64F).var()
                        frames_sampled += 1
                    cap.release()
                
                # Final Tags
                is_blurry = (blur_total / frames_sampled) < 100 if frames_sampled > 0 else False
                
                # Insert to Postgres
                cur.execute("""
                    INSERT INTO assets (file_name, file_path, category, has_face, is_blurry, duration_sec, file_size_mb)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (file, full_path, category, has_face, is_blurry, duration, file_size))
                
                conn.commit() # Commit each file so we don't lose progress

    cur.close()
    conn.close()
    print("Database Update Complete!")

if __name__ == "__main__":
    # 1. Setup DB
    # init_db() 
    # 2. Run Scan
    # scan_and_analyze("F:/Your/Massive/Library")
    pass
