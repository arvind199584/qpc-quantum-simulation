import psycopg2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
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

def train_model():
    print("1. Extracting data from PostgreSQL...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        # Fetching data. For training, we need features (phases) and targets.
        # In this stochastic dataset, every row IS an entanglement event.
        # To train a classifier (Entangled vs Not Entangled), we would need negative examples.
        # Since we only logged positive events, we will train an Autoencoder to learn the manifold
        # of the "Entanglement Phase Space" instead.
        
        query = """
            SELECT s1_cos, s1_sin, s2_cos, s2_sin, s3_cos, s3_sin, 
                   s4_cos, s4_sin, s5_cos, s5_sin, s6_cos, s6_sin
            FROM quantum_entanglement_log;
        """
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")
        return

    if not rows:
        print("No data found to train on.")
        return

    print(f"Loaded {len(rows)} entanglement events.")

    # 2. Data Preparation
    # We will train an Autoencoder. The network will try to reconstruct the input.
    # If a new set of phases can be reconstructed with low error, it belongs to the 
    # "entanglement manifold" (high probability of entanglement).
    X = np.array(rows, dtype=np.float32)
    
    # Split into train and validation sets
    X_train, X_val = train_test_split(X, test_size=0.2, random_state=42)
    
    print(f"Training set: {X_train.shape[0]} samples. Validation set: {X_val.shape[0]} samples.")

    from tensorflow.keras.callbacks import EarlyStopping

    # 3. Build the Digital Twin (Autoencoder Architecture)
    print("\n2. Building the Deep Digital Twin Architecture...")
    model = Sequential([
        Input(shape=(12,)),
        # Encoder (Deeper and Wider for complex manifold learning)
        Dense(128, activation='swish'),
        Dropout(0.2),
        Dense(64, activation='swish'),
        Dense(32, activation='swish'),
        Dense(6, activation='linear', name='bottleneck'), # Expanded bottleneck
        
        # Decoder 
        Dense(32, activation='swish'),
        Dense(64, activation='swish'),
        Dropout(0.2),
        Dense(128, activation='swish'),
        Dense(12, activation='tanh') 
    ])

    # Adjusted learning rate
    model.compile(optimizer=Adam(learning_rate=0.0005), loss='mse', metrics=['mae'])
    model.summary()

    # 4. Training Loop
    print("\n3. Commencing AI Training...")
    
    # Early stopping to prevent overfitting
    early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
    
    history = model.fit(
        X_train, X_train,
        epochs=300, # Increased epochs since we have early stopping
        batch_size=32,
        validation_data=(X_val, X_val),
        callbacks=[early_stop],
        verbose=1 
    )

    # 5. Save the Twin
    model_path = 'quantum_digital_twin_autoencoder.keras'
    model.save(model_path)
    print(f"\nTraining Complete. Digital Twin saved to: {model_path}")
    
    # Analyze Final Loss
    final_loss = history.history['val_loss'][-1]
    print(f"Final Validation MSE Loss: {final_loss:.6f}")
    if final_loss < 0.1:
        print("-> The model successfully learned the topological manifold of entanglement.")
    else:
        print("-> The model is struggling to find a clear pattern. More data or a deeper network might be needed.")

if __name__ == "__main__":
    train_model()
