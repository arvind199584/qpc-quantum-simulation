import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

ROOT_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'daredevil',
    'host': 'localhost',
    'port': '5432'
}

def setup_quantum_db():
    try:
        conn = psycopg2.connect(**ROOT_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Create database
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'quantum';")
        if not cur.fetchone():
            cur.execute('CREATE DATABASE quantum;')
            print('Database "quantum" created.')
        else:
            print('Database "quantum" already exists.')
        
        cur.close()
        conn.close()

        # Create table
        conn = psycopg2.connect(dbname='quantum', user='postgres', password='daredevil', host='localhost', port='5432')
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quantum_phase_routing (
                id SERIAL PRIMARY KEY,
                s1_cos FLOAT8,
                s1_sin FLOAT8,
                s2_cos FLOAT8,
                s2_sin FLOAT8,
                correlation_af FLOAT8,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print('Table "quantum_phase_routing" is ready.')

    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    setup_quantum_db()
