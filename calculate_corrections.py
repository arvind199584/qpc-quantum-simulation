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

def get_angle(cos_val, sin_val):
    deg = math.degrees(math.atan2(sin_val, cos_val))
    return deg if deg >= 0 else deg + 360

def calculate_field_corrections():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Load the latest 20 events to demonstrate the dynamic correction
        query = """
            SELECT qubit_a, qubit_b, 
                   s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin, 
                   s4_cos, s4_sin, s5_cos, s5_sin, s6_cos, s6_sin, event_time
            FROM quantum_entanglement_log
            ORDER BY event_time DESC
            LIMIT 20;
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        print("=== DYNAMIC QUANTUM FIELD AXIS CORRECTION ===")
        print("Assumption: Entangled qubits are always at Local (0, 0, 0).")
        print("Calculating the required Field Axis shift (wobble) to achieve this normalization.\n")
        
        header = f"{'Timestamp / Event':<28} | {'F1 Shift':<9} | {'F2 Shift':<9} | {'F3 Shift':<9} | {'Avg System Wobble':<15}"
        print(header)
        print("-" * len(header))
        
        total_wobbles = []

        for r in rows:
            pair = f"{r[0]} <-> {r[1]}"
            time_str = r[14].strftime("%H:%M:%S.%f")[:-3]
            event_label = f"{time_str} ({pair})"
            
            shifts = []
            # To force the field to 0, the correction is exactly the negative of the measured angle
            # For example, if we measure 90°, the field axis must shift -90° (or +270°) to center it.
            for f_idx in range(6):
                measured_angle = get_angle(r[2 + f_idx*2], r[2 + f_idx*2 + 1])
                # The required correction to make the reading 0
                correction = (360 - measured_angle) % 360 
                shifts.append(correction)
            
            # Calculate the overall "System Wobble" (average shift required across all 6 fields)
            # This represents how far out of alignment the entire universal background is at that moment.
            sys_wobble = np.mean(shifts)
            total_wobbles.append(sys_wobble)
            
            # Displaying corrections for the first 3 fields for brevity
            print(f"{event_label:<28} | {shifts[0]:>7.1f}° | {shifts[1]:>7.1f}° | {shifts[2]:>7.1f}° | {sys_wobble:>13.1f}°")

        avg_universal_wobble = np.mean(total_wobbles)
        print(f"\n--- Analysis ---")
        print(f"Average Universal Field Wobble: {avg_universal_wobble:.1f}°")
        print("Conclusion: To maintain the assumption that entanglement always occurs at the center (0,0,0),")
        print("the underlying quantum fields must be continuously rotating (wobbling) by these exact correction degrees.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    calculate_field_corrections()
