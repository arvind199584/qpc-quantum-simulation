import psycopg2
from psycopg2.extras import RealDictCursor

DB_PARAMS = {
    'dbname': 'quantum',
    'user': 'postgres',
    'password': 'daredevil',
    'host': 'localhost',
    'port': '5432'
}

def display_full_fields():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT qubit_a, qubit_b, 
                   s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin, 
                   s4_cos, s4_sin, s5_cos, s5_sin, s6_cos, s6_sin 
            FROM quantum_entanglement_log 
            ORDER BY event_time DESC 
            LIMIT 5;
        """)
        rows = cur.fetchall()
        
        for i, r in enumerate(rows):
            print(f"\n--- Event {i+1}: {r['qubit_a']} <-> {r['qubit_b']} ---")
            print(f"Field 1 (EM):     ({r['s1_cos']:.4f}, {r['s1_sin']:.4f})")
            print(f"Field 2 (Higgs):  ({r['s2_cos']:.4f}, {r['s2_sin']:.4f})")
            print(f"Field 3 (Strong): ({r['s3_cos']:.4f}, {r['s3_sin']:.4f})")
            print(f"Field 4 (Weak):   ({r['s4_cos']:.4f}, {r['s4_sin']:.4f})")
            print(f"Field 5 (Lepton): ({r['s5_cos']:.4f}, {r['s5_sin']:.4f})")
            print(f"Field 6 (Gravity):({r['s6_cos']:.4f}, {r['s6_sin']:.4f})")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    display_full_fields()
