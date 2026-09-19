import duckdb, os
import numpy as np
from blade_anomaly import calculate_mad_anomaly

db_path = os.path.expanduser('~/genesis_node_00/data/ticks.duckdb')
conn = duckdb.connect(db_path)

# Initialize Schema
conn.execute('CREATE TABLE IF NOT EXISTS tick_stream (timestamp TIMESTAMP, symbol VARCHAR, price DOUBLE)')

# Insert Sample Real-Time Feed Data
conn.execute("""
INSERT INTO tick_stream VALUES 
    (NOW(), 'BTC/USD', 100.1),
    (NOW(), 'BTC/USD', 100.2),
    (NOW(), 'BTC/USD', 100.15),
    (NOW(), 'BTC/USD', 100.3),
    (NOW(), 'BTC/USD', 125.4),
    (NOW(), 'BTC/USD', 100.1)
""")

# Query Time-Series Rows Directly
results = conn.execute("SELECT price FROM tick_stream WHERE symbol = 'BTC/USD' ORDER BY timestamp DESC LIMIT 100").fetchall()
prices = [row[0] for row in results]

# Run Blade Anomaly Detection on SQL Query Output
anomalies = calculate_mad_anomaly(prices)
flagged = [prices[i] for i, is_anom in enumerate(anomalies) if is_anom]

print(f'[DUCKDB MEMORY] Total Ticks Ingested: {len(prices)}')
print(f'[BLADE ENGINE] Anomalies Flagged from DB: {flagged}')
conn.close()
