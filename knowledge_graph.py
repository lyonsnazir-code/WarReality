import json
from datetime import datetime
from pathlib import Path

LEDGER_FILE = Path("knowledge_graph.json")

def log_event(anomalies, headlines):
    """Logs anomalies and associated intel into a persistent local knowledge graph ledger."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "anomalies": anomalies,
        "intel": headlines
    }
    
    data = []
    if LEDGER_FILE.exists():
        try:
            with open(LEDGER_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
            
    data.append(entry)
    
    with open(LEDGER_FILE, "w") as f:
        json.dump(data, f, indent=4)
        
    print(f"   --> [KNOWLEDGE GRAPH] Event committed to local ledger. Total entries: {len(data)}")