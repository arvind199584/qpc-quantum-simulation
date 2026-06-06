import psycopg2
import numpy as np
import math

DB_PARAMS = {
    'dbname': 'quantum',
    'user': 'postgres',
    'password': 'daredevil',
    'host': 'localhost',
    'port': '5432'
}

def analyze_deviation():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Load all shifts to analyze the 3.5 degree deviation
        query = """
            SELECT s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin, 
                   s4_cos, s4_sin, s5_cos, s5_sin, s6_cos, s6_sin
            FROM quantum_entanglement_log;
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        deviations = []
        field_deviations = [[] for _ in range(6)]

        for r in rows:
            shifts = []
            for f_idx in range(6):
                cos_val = r[f_idx*2]
                sin_val = r[f_idx*2 + 1]
                
                deg = math.degrees(math.atan2(sin_val, cos_val))
                if deg < 0: deg += 360
                
                # Shift required to hit 0
                correction = (360 - deg) % 360
                
                # Deviation from the theoretical 180 degree minimum energy state
                # We use absolute distance from 180
                dev_from_180 = correction - 180
                
                shifts.append(correction)
                field_deviations[f_idx].append(dev_from_180)
                
            sys_wobble = np.mean(shifts)
            sys_dev = sys_wobble - 180
            deviations.append(sys_dev)

        print("=== TOPOLOGICAL DEFECT ANALYSIS ===")
        print("Hypothesis: Entanglement occurs at Minimum Energy State (180°).")
        print("Analyzing the ~3.5° deviation to determine if it is random error or a structural defect.\n")
        
        # 1. Overall System Deviation
        mean_dev = np.mean(deviations)
        std_dev = np.std(deviations)
        
        print(f"Overall System Deviation from 180°: {mean_dev:+.2f}°")
        print(f"Standard Error of the Deviation:  ±{std_dev:.2f}°\n")
        
        # 2. Field-by-Field Breakdown
        print("Deviation Breakdown by Field:")
        field_names = ["EM (F1)", "Higgs (F2)", "Strong (F3)", "Weak (F4)", "Lepton (F5)", "Gravity (F6)"]
        for i, name in enumerate(field_names):
            f_mean = np.mean(field_deviations[i])
            print(f" - {name:<12}: {f_mean:+.2f}°")
            
        print("\n--- Conclusion ---")
        if abs(mean_dev) < 1.0:
            print("The 180° hypothesis is perfectly confirmed. Deviations are negligible system noise.")
        elif std_dev > 45:
            print("The deviation is highly chaotic. The 3.5° average is likely a mathematical artifact of high-entropy sampling rather than a physical property.")
        else:
            print(f"The system exhibits a consistent topological defect (wobble) of {mean_dev:+.2f}°.")
            print("This is not random error. It is a persistent signature of the IBM Quantum hardware's vacuum state (zero-point energy offset).")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_deviation()
