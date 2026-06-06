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

def analyze():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Load all 6 fields and qubit pairs
        query = """
            SELECT qubit_a, qubit_b, 
                   s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin, 
                   s4_cos, s4_sin, s5_cos, s5_sin, s6_cos, s6_sin
            FROM quantum_entanglement_log;
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        total = len(rows)
        pair_frequency = defaultdict(int)
        field_angles = [[] for _ in range(6)]
        pair_to_angles = defaultdict(lambda: [[] for _ in range(6)])
        
        for r in rows:
            pair = f"{r[0]} <-> {r[1]}"
            pair_frequency[pair] += 1
            
            for f_idx in range(6):
                angle = get_angle(r[2 + f_idx*2], r[2 + f_idx*2 + 1])
                field_angles[f_idx].append(angle)
                pair_to_angles[pair][f_idx].append(angle)

        print(f"=== QUANTUM PATTERN ANALYSIS REPORT ===")
        print(f"Total Observations: {total}")
        
        # 1. FIELD PHASE DISTRIBUTION
        print("\n1. Fundamental Field Phase Distributions:")
        field_names = ["EM (F1)", "Higgs (F2)", "Strong (F3)", "Weak (F4)", "Lepton (F5)", "Gravity (F6)"]
        for i, name in enumerate(field_names):
            mean_ang = np.mean(field_angles[i])
            std_ang = np.std(field_angles[i])
            print(f" - {name:<12}: Mean {mean_ang:>6.1f}°, StdDev {std_ang:>5.1f}°")

        # 2. TOP INTERACTING QUBIT PAIRS
        print("\n2. Top 5 Entangling Pairs (Activity Hubs):")
        sorted_pairs = sorted(pair_frequency.items(), key=lambda x: x[1], reverse=True)
        for pair, count in sorted_pairs[:5]:
            print(f" - {pair:<25}: {count} events ({(count/total)*100:.1f}%)")

        # 3. RESONANCE DISCOVERY (Pairs with consistent field phases)
        print("\n3. Resonance Discovery (Stable Phase Windows):")
        resonances_found = 0
        for pair, f_data in pair_to_angles.items():
            if pair_frequency[pair] >= 5: # Only look at active pairs
                for f_idx in range(6):
                    std = np.std(f_data[f_idx])
                    if std < 30: # High consistency threshold
                        mean = np.mean(f_data[f_idx])
                        print(f" [RESONANCE] {pair:<22} locked to {field_names[f_idx]} at {mean:.1f}° (±{std:.1f}°)")
                        resonances_found += 1
        
        if resonances_found == 0:
            print(" - No strong phase locks found in current dataset (system is in high-entropy exploration).")

        # 4. FIELD COUPLING MATRIX (Simplified)
        print("\n4. Field Interaction Correlations:")
        # Check if Field A moving predicts Field B moving
        for i in range(6):
            for j in range(i + 1, 6):
                corr = np.corrcoef(field_angles[i], field_angles[j])[0, 1]
                if abs(corr) > 0.1: # Significant coupling
                    state = "Constructive" if corr > 0 else "Destructive"
                    print(f" - {field_names[i]} <-> {field_names[j]}: {state} Interference (Corr: {corr:.2f})")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Analysis Error: {e}")

if __name__ == "__main__":
    analyze()
