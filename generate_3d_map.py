import psycopg2
import numpy as np
import math
import os
from collections import defaultdict
import plotly.graph_objects as go

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

def generate_3d_map():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Load All Data
        query = """
            SELECT qubit_a, qubit_b, 
                   s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin
            FROM quantum_entanglement_log;
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        # Define NEW Zero Reference Pairs
        new_zero_pairs = ['Qubit 62 <-> Qubit 63', 'Qubit 92 <-> Qubit 142']
        
        # Calculate the NEW Bias (Zero Point)
        new_zero_offsets = [[] for _ in range(3)]
        for r in rows:
            pair = f"{r[0]} <-> {r[1]}"
            if pair in new_zero_pairs:
                for f_idx in range(3):
                    angle = get_angle(r[2 + f_idx*2], r[2 + f_idx*2 + 1])
                    new_zero_offsets[f_idx].append(angle)
        
        # New Reference Zero
        new_biases = [np.mean(offsets) if offsets else 0 for offsets in new_zero_offsets]
        
        # Aggregate average positions for each qubit pair
        pair_data = defaultdict(lambda: [[] for _ in range(3)])
        
        for r in rows:
            pair = f"{r[0]} <-> {r[1]}"
            for f_idx in range(3):
                actual = get_angle(r[2 + f_idx*2], r[2 + f_idx*2 + 1])
                aligned = normalize_angle(actual - new_biases[f_idx])
                pair_data[pair][f_idx].append(aligned)
                
        # Prepare data for 3D plot
        labels = []
        x_f1 = []
        y_f2 = []
        z_f3 = []
        sizes = []
        colors = []
        
        old_hubs = ['Qubit 4 <-> Qubit 28', 'Qubit 10 <-> Qubit 15', 'Qubit 62 <-> Qubit 44']
        
        for pair, angles in pair_data.items():
            count = len(angles[0])
            avg_f1 = np.mean(angles[0])
            avg_f2 = np.mean(angles[1])
            avg_f3 = np.mean(angles[2])
            
            labels.append(f"{pair} (Events: {count})")
            x_f1.append(avg_f1)
            y_f2.append(avg_f2)
            z_f3.append(avg_f3)
            
            # Highlight hubs
            if pair in new_zero_pairs:
                colors.append('red')
                sizes.append(15)
            elif pair in old_hubs:
                colors.append('orange')
                sizes.append(12)
            else:
                colors.append('blue')
                sizes.append(count * 2 + 3) # Scale by frequency

        # Create Interactive 3D Scatter Plot
        fig = go.Figure(data=[go.Scatter3d(
            x=x_f1,
            y=y_f2,
            z=z_f3,
            mode='markers',
            marker=dict(
                size=sizes,
                color=colors,
                opacity=0.8,
                line=dict(width=0.5, color='white')
            ),
            text=labels,
            hoverinfo='text'
        )])

        fig.update_layout(
            title="3D Quantum Topological Alignment (Fields 1, 2, 3)",
            scene=dict(
                xaxis_title='Field 1 Phase (°)',
                yaxis_title='Field 2 Phase (°)',
                zaxis_title='Field 3 Phase (°)',
                xaxis=dict(range=[0, 360]),
                yaxis=dict(range=[0, 360]),
                zaxis=dict(range=[0, 360])
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )
        
        file_name = "3D_Quantum_Map.html"
        fig.write_html(file_name)
        print(f"Success! 3D Map generated: {os.path.abspath(file_name)}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_3d_map()
