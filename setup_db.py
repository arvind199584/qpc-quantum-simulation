import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

ROOT_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "daredevil",
    "host": "localhost",
    "port": "5432"
}

def create_database():
    try:
        conn = psycopg2.connect(**ROOT_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'Daredevil Songs';")
        exists = cur.fetchone()
        db_name = "Daredevil Songs"
        if not exists:
            cur.execute(f'CREATE DATABASE "{db_name}";')
            print(f"Database '{db_name}' created.")
        cur.close()
        conn.close()

        # Reconnect to the target DB
        NEW_DB_CONFIG = ROOT_CONFIG.copy()
        NEW_DB_CONFIG["dbname"] = db_name
        conn = psycopg2.connect(**NEW_DB_CONFIG)
        cur = conn.cursor()
        
        # Check for pgvector
        has_vector = False
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            print("pgvector enabled.")
            has_vector = True
        except Exception:
            conn.rollback()
            print("Notice: pgvector not found. Using float8[] fallback.")
            has_vector = False
        
        vector_type = "VECTOR(384)" if has_vector else "float8[]"
        
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS audio_index (
                id SERIAL PRIMARY KEY,
                file_name TEXT,
                file_path TEXT UNIQUE,
                file_hash TEXT,
                semantic_vec {vector_type},
                tags JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_hash ON audio_index(file_hash);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_path_audio ON audio_index(file_path);")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Setup Complete.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_database()
