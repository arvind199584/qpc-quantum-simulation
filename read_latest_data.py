import psycopg2
from psycopg2.extras import RealDictCursor

DB_PARAMS = {
    'dbname': 'quantum',
    'user': 'postgres',
    'password': 'daredevil',
    'host': 'localhost',
    'port': '5432'
}

def display_latest():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT qubit_a, qubit_b, s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin 
            FROM quantum_entanglement_log 
            ORDER BY event_time DESC 
            LIMIT 15;
        """)
        rows = cur.fetchall()
        
        header = f"{'Entangled Qubits':<22} | {'Field 1 (Cos, Sin)':<22} | {'Field 2 (Cos, Sin)':<22}"
        print("\n" + header)
        print("-" * len(header))
        
        for r in rows:
            pair = f"{r['qubit_a']} <-> {r['qubit_b']}"
            f1 = f"({r['s1_cos']:.4f}, {r['s1_sin']:.4f})"
            f2 = f"({r['s2_cos']:.4f}, {r['s2_sin']:.4f})"
            print(f"{pair:<22} | {f1:<22} | {f2:<22}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    display_latest()
