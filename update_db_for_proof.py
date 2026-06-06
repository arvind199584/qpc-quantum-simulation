import psycopg2

def update_schema_for_proof():
    try:
        conn = psycopg2.connect(dbname='quantum', user='postgres', password='daredevil', host='localhost', port='5432')
        cur = conn.cursor()
        
        # Add columns for Job ID and Precision Timestamp
        cur.execute("ALTER TABLE quantum_entanglement_log ADD COLUMN IF NOT EXISTS job_id TEXT;")
        cur.execute("ALTER TABLE quantum_entanglement_log ADD COLUMN IF NOT EXISTS precision_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database schema updated for Quantum Proof (Job ID & Timestamps).")
    except Exception as e:
        print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema_for_proof()
