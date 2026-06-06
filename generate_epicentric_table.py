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
    # Ensure angle stays within 0-360
    return angle % 360

def generate_epicentric_table():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # 1. Identify Epicenter Pairs (Activity Hubs)
        # We'll use the pairs identified in the previous analysis
        epicenter_pairs = ['Qubit 4 <-> Qubit 28', 'Qubit 10 <-> Qubit 15', 'Qubit 62 <-> Qubit 44']
        
        # 2. Calculate the Phase Bias (Epicenter) for each field based on these pairs
        # We query the database specifically for these pairs to find their 'natural' phase
        query = """
            SELECT qubit_a, qubit_b, 
                   s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin, 
                   s4_cos, s4_sin, s5_cos, s5_sin, s6_cos, s6_sin
            FROM quantum_entanglement_log;
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        epicenter_offsets = [[] for _ in range(6)]
        
        for r in rows:
            pair = f"{r[0]} <-> {r[1]}"
            if pair in epicenter_pairs:
                for f_idx in range(6):
                    angle = get_angle(r[2 + f_idx*2], r[2 + f_idx*2 + 1])
                    epicenter_offsets[f_idx].append(angle)
        
        # Calculate mean bias for each field across all epicenter pairs
        # This becomes our "0 degree" reference
        biases = [np.mean(offsets) for offsets in epicenter_offsets]
        
        print("=== EPICENTRIC PHASE ALIGNMENT ===")
        print("Assuming Active Pairs (4-28, 10-15, 62-44) represent the 0° plane.\n")
        print("Calculated Field Reference Biases (Actual -> 0° Mapping):")
        field_names = ["EM (F1)", "Higgs (F2)", "Strong (F3)", "Weak (F4)", "Lepton (F5)", "Gravity (F6)"]
        for i, name in enumerate(field_names):
            print(f" - {name}: {biases[i]:.2f}° is now EPICENTER (0°)")

        # 3. Generate Aligned Data Table
        print("\n=== EPICENTRIC DATA TABLE (Aligned Angles) ===")
        header = f"{'Entangled Pair':<25} | {'F1 (Rel)':<8} | {'F2 (Rel)':<8} | {'F3 (Rel)':<8} | {'F4 (Rel)':<8}"
        print(header)
        print("-" * len(header))
        
        # We'll show the last 15 entries with aligned angles
        # Aligned Angle = Actual Angle - Epicenter Bias
        for i, r in enumerate(rows[-20:]):
            pair = f"{r[0]} <-> {r[1]}"
            aligned_angles = []
            for f_idx in range(6):
                actual = get_angle(r[2 + f_idx*2], r[2 + f_idx*2 + 1])
                aligned = normalize_angle(actual - biases[f_idx])
                aligned_angles.append(aligned)
            
            print(f"{pair:<25} | {aligned_angles[0]:>6.1f}° | {aligned_angles[1]:>6.1f}° | {aligned_angles[2]:>6.1f}° | {aligned_angles[3]:>6.1f}°")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_epicentric_table()
