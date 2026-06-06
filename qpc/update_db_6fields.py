import psycopg2

def update_schema():
    try:
        conn = psycopg2.connect(dbname='quantum', user='postgres', password='daredevil', host='localhost', port='5432')
        cur = conn.cursor()
        
        # Add columns for 6 fields (s1 and s2 already exist)
        for i in range(3, 7):
            cur.execute(f"ALTER TABLE quantum_phase_routing ADD COLUMN IF NOT EXISTS s{i}_cos FLOAT8;")
            cur.execute(f"ALTER TABLE quantum_phase_routing ADD COLUMN IF NOT EXISTS s{i}_sin FLOAT8;")
            
        conn.commit()
        cur.close()
        conn.close()
        print("Database schema updated successfully for 6 fields.")
    except Exception as e:
        print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
