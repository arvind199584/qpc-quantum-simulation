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

def generate_heatmap():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("SELECT s1_cos, s1_sin, s2_cos, s2_sin FROM quantum_entanglement_log;")
        rows = cur.fetchall()
        
        # Grid size (e.g., 10x10 bins for 360 degrees)
        bins = 12
        grid = np.zeros((bins, bins))
        
        for r in rows:
            # Field 1 angle
            f1_rad = math.atan2(r[1], r[0])
            f1_deg = math.degrees(f1_rad)
            if f1_deg < 0: f1_deg += 360
            
            # Field 2 angle
            f2_rad = math.atan2(r[3], r[2])
            f2_deg = math.degrees(f2_rad)
            if f2_deg < 0: f2_deg += 360
            
            # Map to grid
            x = int(f1_deg / (360 / bins))
            y = int(f2_deg / (360 / bins))
            grid[y, x] += 1

        print("\n=== ENTANGLEMENT HEATMAP (Field 1 vs Field 2) ===")
        print("X-Axis: Field 1 (0° to 360°) | Y-Axis: Field 2 (0° to 360°)")
        print("Scale: . (low) to # (high)\n")
        
        # Labels
        header = "      " + " ".join([f"{i*30:>3}" for i in range(bins)])
        print(header)
        print("      " + "-" * (bins * 4))
        
        symbols = " .:-=+*#%@"
        max_val = np.max(grid) if np.max(grid) > 0 else 1
        
        for i in range(bins):
            row_label = f"{i*30:>3}° |"
            row_str = row_label
            for j in range(bins):
                val = grid[i, j]
                symbol_idx = int((val / max_val) * (len(symbols) - 1))
                row_str += f"  {symbols[symbol_idx]} "
            print(row_str)
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_heatmap()
