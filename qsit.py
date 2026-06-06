import numpy as np
import psycopg2
import os
import json
import time
from datetime import datetime
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ---------------------------------------------------------
# 0. AUTHENTICATION & BACKEND SETUP
# ---------------------------------------------------------
# TOGGLE: Set to True for the final 4-minute IBM session
USE_CLOUD = True 

def get_ibm_service():
    if not os.path.exists('apikey.json'): return None
    try:
        with open('apikey.json', 'r') as f:
            data = json.load(f)
            print(f"Connecting to IBM Quantum for: {data.get('name', 'Unknown')}...")
            return QiskitRuntimeService(channel="ibm_quantum_platform", token=data.get('apikey'))
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

if USE_CLOUD:
    service = get_ibm_service()
    if service:
        try:
            # Manually specifying a known operational backend from our recent check
            backend = service.backend("ibm_marrakesh")
            print(f">>> MODE: IBM CLOUD HARDWARE ({backend.name}) <<<")
        except Exception as e:
            print(f"Cloud Selection Error: {e}. Falling back to Local.")
            backend = AerSimulator()
            USE_CLOUD = False
    else:
        print("No IBM Service available. Falling back to Local.")
        backend = AerSimulator()
        USE_CLOUD = False
else:
    backend = AerSimulator()
    print(">>> MODE: LOCAL OFFLINE TEST (100 Qubits) <<<")

# Architecture Setup
if USE_CLOUD:
    # Use actual hardware qubit count
    n_total_qubits = backend.num_qubits 
else:
    # Cap local simulation to backend limit (29) to avoid coupling map errors
    n_total_qubits = 29 

n_active = n_total_qubits 
n_fields_qubits = 3
n_obs_qubits = n_active - n_fields_qubits

print(f"Architecture: {n_active} Qubits Active ({n_fields_qubits} fields, {n_obs_qubits} observation).")

# ---------------------------------------------------------
# 1. DATABASE LOGGING (WITH PROOF)
# ---------------------------------------------------------
DB_PARAMS = {
    "dbname": "quantum",
    "user": "postgres",
    "password": "daredevil",
    "host": "localhost",
    "port": "5432"
}

def log_event_with_proof(phases, q_a, q_b, job_id):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        query = """
            INSERT INTO quantum_entanglement_log 
            (s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin, s4_cos, s4_sin, s5_cos, s5_sin, s6_cos, s6_sin, 
             qubit_a, qubit_b, job_id, precision_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        clean_phases = [float(p) for p in phases]
        now = datetime.now()
        cursor.execute(query, (*clean_phases, str(q_a), str(q_b), job_id, now))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Log Error: {e}")

# ---------------------------------------------------------
# 2. THE QUANTUM EXPERIMENT LOOP
# ---------------------------------------------------------
# SET DURATION: Exactly 4:48 remaining
DURATION = 288 
start_time = time.time()


iteration = 0

sampler = Sampler(mode=backend)

print(f"\nStarting Monitoring for {DURATION} seconds...")

while (time.time() - start_time) < DURATION:
    angles = np.random.uniform(0, 2 * np.pi, 6)
    phases = []
    for a in angles:
        phases.extend([np.cos(a), np.sin(a)])
    
    pool_indices = list(range(n_fields_qubits, n_active))
    q_pair = np.random.choice(pool_indices, 2, replace=False)
    
    # Construct circuit
    qc = QuantumCircuit(n_active, 2)
    for i in range(n_fields_qubits):
        qc.ry(angles[i*2], i)
        qc.rx(angles[i*2 + 1], i)
    
    qc.h(q_pair[0])
    qc.cx(q_pair[0], q_pair[1])
    qc.measure([q_pair[0], q_pair[1]], [0, 1])
    
    try:
        # Optimization level 1 for speed
        isa_circuit = transpile(qc, backend, optimization_level=1)
        job = sampler.run([isa_circuit], shots=1)
        
        # Capture Real or Mock Job ID
        if USE_CLOUD:
            current_job_id = job.job_id()
        else:
            current_job_id = f"OFFLINE_TEST_{int(time.time())}_{iteration}"
        
        log_event_with_proof(phases, f"Qubit {q_pair[0]}", f"Qubit {q_pair[1]}", current_job_id)
        
        elapsed = time.time() - start_time
        print(f"[{elapsed:.1f}s] Event {iteration} | Job: {current_job_id[:16]} | Pair: {q_pair[0]}-{q_pair[1]}")
    except Exception as e:
        print(f"Execution Error: {e}")
        break # Exit on error to avoid looping failures
    
    iteration += 1
    if not USE_CLOUD:
        time.sleep(0.01) # Speed for local test

print(f"\nSession Stop. Total Events: {iteration}")
