import psycopg2
import numpy as np
import math
from collections import defaultdict

DB_PARAMS = {
    'dbname': 'quantum',
    'user': 'postgres',
    'password': 'daredevil',
    'host': 'localhost',
    'port': '5432'
}

def analyze_correlations():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("SELECT qubit_a, qubit_b, s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin, s4_cos, s4_sin, s5_cos, s5_sin, s6_cos, s6_sin FROM quantum_entanglement_log;")
        rows = cur.fetchall()
        
        pair_data = defaultdict(list)
        
        print(f"{'Qubit Pair':<20} | {'F1 Angle':<8} | {'F2 Angle':<8} | {'F3 Angle':<8}")
        print("-" * 60)
        
        for i, r in enumerate(rows):
            # Convert cos/sin to degrees (0-360)
            angles = []
            for j in range(2, 14, 2):
                rad = math.atan2(r[j+1], r[j])
                deg = math.degrees(rad)
                if deg < 0: deg += 360
                angles.append(deg)
            
            pair = f"{r[0]} <-> {r[1]}"
            pair_data[pair].append(angles)
            
            if i < 10: # Show first 10 for the user to see the translation
                print(f"{pair:<20} | {angles[0]:>6.1f}° | {angles[1]:>6.1f}° | {angles[2]:>6.1f}°")

        # Basic Correlation Discovery
        print("\n--- Correlation Discovery: Top Entanglement Hotspots ---")
        for pair, all_angles in pair_data.items():
            if len(all_angles) > 3: # Only look at pairs that entangled multiple times
                avg_f1 = np.mean([a[0] for a in all_angles])
                std_f1 = np.std([a[0] for a in all_angles])
                if std_f1 < 45: # If the angle is consistent (low standard deviation)
                    print(f"Match Found: {pair} entangles consistently when Field 1 is near {avg_f1:.1f}°")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_correlations()
