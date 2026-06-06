import psycopg2

def create_log_table():
    try:
        conn = psycopg2.connect(dbname='quantum', user='postgres', password='daredevil', host='localhost', port='5432')
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quantum_entanglement_log (
                id SERIAL PRIMARY KEY,
                s1_cos FLOAT8, s1_sin FLOAT8,
                s2_cos FLOAT8, s2_sin FLOAT8,
                s3_cos FLOAT8, s3_sin FLOAT8,
                s4_cos FLOAT8, s4_sin FLOAT8,
                s5_cos FLOAT8, s5_sin FLOAT8,
                s6_cos FLOAT8, s6_sin FLOAT8,
                qubit_a TEXT,
                qubit_b TEXT,
                event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("New entanglement log table created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_log_table()
