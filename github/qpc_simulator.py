import numpy as np
import json
import math
import time
import os

# --- CONFIGURATION ---
VOLUME_SIZE = 100.0
FPS = 30
TOLERANCE_DEG = 1.2
CONFIG_FILE = "qpc_config.json"

def load_config():
    default = {
        "num_qubits": 10,
        "em_freq": 1.0,
        "higgs_freq": 0.8,
        "strong_freq": 1.2,
        "weak_freq": 0.5,
        "lepton_freq": 1.5,
        "field_dirs": [
            [1.0, 0.2, 0.1],   # EM
            [-0.1, 1.0, 0.3],  # Higgs
            [0.4, -0.4, 1.0],  # Strong
            [-1.0, -0.2, 0.5], # Weak
            [0.2, 0.7, -1.0]   # Lepton
        ]
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return {**default, **json.load(f)}
        except:
            return default
    return default

def simulate():
    print(f"Starting QPC Multi-Field Simulation...")
    print("Press Ctrl+C to stop.")
    
    current_config = load_config()
    num_qubits = current_config["num_qubits"]
    np.random.seed(42)
    qubit_coords = np.random.uniform(-VOLUME_SIZE/2, VOLUME_SIZE/2, (num_qubits, 3))

    frame = 0
    try:
        while True:
            new_config = load_config()
            if new_config["num_qubits"] != num_qubits:
                num_qubits = new_config["num_qubits"]
                qubit_coords = np.random.uniform(-VOLUME_SIZE/2, VOLUME_SIZE/2, (num_qubits, 3))
            current_config = new_config
            
            freqs = [
                current_config["em_freq"],
                current_config["higgs_freq"],
                current_config["strong_freq"],
                current_config["weak_freq"],
                current_config["lepton_freq"]
            ]
            dirs = np.array(current_config["field_dirs"])
            
            all_frames = []
            for _ in range(30): # 1 second batches
                t = frame / FPS
                frame_events = []
                
                # Calculate phases for all 5 fields
                all_phases = []
                all_grid_phases = []
                
                grid = np.linspace(-VOLUME_SIZE/2, VOLUME_SIZE/2, 10)
                gx, gy = np.meshgrid(grid, grid)
                gz = np.zeros_like(gx)
                points = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)

                for f_idx in range(5):
                    k = (dirs[f_idx] / np.linalg.norm(dirs[f_idx])) * (2 * np.pi / (VOLUME_SIZE / 2))
                    omega = 2 * np.pi * freqs[f_idx]
                    
                    # Qubit phases
                    dot_product = np.dot(qubit_coords, k)
                    p = (np.degrees(np.arcsin(np.sin(omega * t - dot_product))) + 360) % 360
                    all_phases.append(p)
                    
                    # Grid phases for visualization (10x10 slice)
                    grid_p = (np.sin(omega * t - np.dot(points, k)))
                    all_grid_phases.append(grid_p.reshape(10, 10).tolist())

                # Entanglement scan (COMMON QUANTUM FIELD MINIMUM ENERGY MODEL)
                # We sum the values of all active fields at each qubit coordinate.
                # Entanglement occurs when the 'Differential Energy' between two qubits 
                # reaches a zero-state (destructive interference / minimum energy).
                active_mask = current_config.get("active_fields", [True] * 5)
                
                # 1. Calculate the 'Common Field Value' at each qubit
                # This is the superposition: Sum(sin(phi_i))
                common_field_values = np.zeros(num_qubits)
                active_count = 0
                for f_idx in range(5):
                    if active_mask[f_idx]:
                        # Using the sine of the phase to get the field amplitude (-1 to 1)
                        common_field_values += np.sin(np.radians(all_phases[f_idx]))
                        active_count += 1
                
                # 2. Identify Minimum Energy Pairs
                if active_count > 0:
                    for i in range(num_qubits):
                        for j in range(i + 1, num_qubits):
                            # The 'Zero-Point' condition: 
                            # Both qubits are at a similar low-energy state in the combined field
                            # OR their combined amplitude is near zero
                            combined_amplitude_diff = abs(common_field_values[i] - common_field_values[j])
                            
                            # We use a normalized threshold for 'near zero'
                            if combined_amplitude_diff < (0.05 * active_count): 
                                frame_events.append({"p1": i, "p2": j})

                all_frames.append({
                    "t": t,
                    "events": frame_events,
                    "fields": all_grid_phases
                })
                frame += 1

            sim_data = {
                "qubits": qubit_coords.tolist(),
                "frames": all_frames,
                "metadata": {"fps": FPS, "volume": VOLUME_SIZE}
            }
            with open("qpc_sim_data.json", "w") as f:
                json.dump(sim_data, f)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    simulate()
