import json
from pathlib import Path

LEDGER_FILE = Path("knowledge_graph.json")

def run_backtest():
    """Runs a historical simulation pass over logged knowledge graph anomalies."""
    print("[BACKTESTER] Initializing historical simulation engine...")
    
    if not LEDGER_FILE.exists():
        print("[BACKTESTER ERROR] No knowledge graph ledger found. Run the daemon first to collect data.")
        return
        
    try:
        with open(LEDGER_FILE, "r") as f:
            ledger = json.load(f)
    except json.JSONDecodeError:
        print("[BACKTESTER ERROR] Ledger file is corrupted or empty.")
        return
        
    total_events = len(ledger)
    if total_events == 0:
        print("[BACKTESTER] Ledger is empty. No telemetry to analyze.")
        return
        
    print(f"[BACKTESTER] Analyzing {total_events} recorded telemetry blocks...")
    
    # Simulation metrics calculation
    anomaly_magnitudes = []
    intel_hit_count = 0
    
    for entry in ledger:
        anomalies = entry.get("anomalies", [])
        intel = entry.get("intel", [])
        
        if anomalies:
            anomaly_magnitudes.extend(anomalies)
        if intel:
            intel_hit_count += len(intel)
            
    avg_magnitude = sum(anomaly_magnitudes) / len(anomaly_magnitudes) if anomaly_magnitudes else 0.0
    
    print("\n--- [BACKTEST REPORT SUMMARY] ---")
    print(f"Total Telemetry Cycles Evaluated : {total_events}")
    print(f"Average Anomaly Magnitude Index  : {avg_magnitude:.4f}")
    print(f"Total OSINT Intel Vectors Bound  : {intel_hit_count}")
    print(f"System State Stability Index     : {(100.0 - (avg_magnitude % 10)) / 100 * 100:.2f}%")
    print("---------------------------------\n")

if __name__ == "__main__":
    run_backtest()