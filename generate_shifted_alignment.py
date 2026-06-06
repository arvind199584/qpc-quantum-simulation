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

def get_angle(cos_val, sin_val):
    deg = math.degrees(math.atan2(sin_val, cos_val))
    return deg if deg >= 0 else deg + 360

def normalize_angle(angle):
    return angle % 360

def generate_shifted_alignment():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # 1. Load All Data
        query = """
            SELECT qubit_a, qubit_b, 
                   s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin, 
                   s4_cos, s4_sin, s5_cos, s5_sin, s6_cos, s6_sin
            FROM quantum_entanglement_log;
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        # 2. Define NEW Zero Reference Pairs
        new_zero_pairs = ['Qubit 62 <-> Qubit 63', 'Qubit 92 <-> Qubit 142']
        
        # 3. Calculate the NEW Bias (Zero Point)
        new_zero_offsets = [[] for _ in range(6)]
        for r in rows:
            pair = f"{r[0]} <-> {r[1]}"
            if pair in new_zero_pairs:
                for f_idx in range(6):
                    angle = get_angle(r[2 + f_idx*2], r[2 + f_idx*2 + 1])
                    new_zero_offsets[f_idx].append(angle)
        
        # New Reference Zero
        new_biases = [np.mean(offsets) for offsets in new_zero_offsets]
        
        print("=== MULTI-TIER TOPOLOGICAL ALIGNMENT ===")
        print("NEW Reference Zero (0°): Qubit 62-63 & Qubit 92-142\n")
        
        # 4. Display the Aligned Coordinates
        # We will show the NEW Zero pairs, then the OLD 0.2% pairs to see their relative shift.
        old_hubs = ['Qubit 4 <-> Qubit 28', 'Qubit 10 <-> Qubit 15', 'Qubit 62 <-> Qubit 44']
        
        header = f"{'Entangled Pair':<25} | {'Status':<10} | {'F1 (Rel)':<8} | {'F2 (Rel)':<8} | {'F3 (Rel)':<8}"
        print(header)
        print("-" * len(header))
        
        # Show New Zeroes
        for pair in new_zero_pairs:
            # Finding one instance to show
            for r in rows:
                if f"{r[0]} <-> {r[1]}" == pair:
                    aligned = []
                    for f_idx in range(6):
                        actual = get_angle(r[2 + f_idx*2], r[2 + f_idx*2 + 1])
                        aligned.append(normalize_angle(actual - new_biases[f_idx]))
                    print(f"{pair:<25} | {'NEW ZERO':<10} | {aligned[0]:>6.1f}° | {aligned[1]:>6.1f}° | {aligned[2]:>6.1f}°")
                    break
                    
        # Show Old Hubs (to prove relative distance is same)
        for pair in old_hubs:
            # Finding one instance to show
            for r in rows:
                if f"{r[0]} <-> {r[1]}" == pair:
                    aligned = []
                    for f_idx in range(6):
                        actual = get_angle(r[2 + f_idx*2], r[2 + f_idx*2 + 1])
                        aligned.append(normalize_angle(actual - new_biases[f_idx]))
                    print(f"{pair:<25} | {'OLD HUB':<10} | {aligned[0]:>6.1f}° | {aligned[1]:>6.1f}° | {aligned[2]:>6.1f}°")
                    break

        print("\nNote: The relative angles between Hubs are preserved, but the system is now anchored to the 62-63/92-142 plane.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_shifted_alignment()
