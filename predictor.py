import json
from pathlib import Path

LEDGER_FILE = Path("knowledge_graph.json")

def evaluate_market_signals():
    """Evaluates local knowledge graph intelligence to gauge tactical market probabilities."""
    print("[PREDICTOR] Scanning intelligence ledgers for market signals...")
    
    if not LEDGER_FILE.exists():
        print("[PREDICTOR ERROR] No telemetry ledger found.")
        return
        
    with open(LEDGER_FILE, "r") as f:
        ledger = json.load(f)
        
    if not ledger:
        print("[PREDICTOR] Ledger is empty.")
        return
        
    recent_entries = ledger[-5:] # Look at the last 5 ticks
    sentiment_score = 0
    
    for entry in recent_entries:
        intel_list = entry.get("intel", [])
        for item in intel_list:
            title = item.get("title", "").lower()
            # Simple keyword weight heuristic
            if any(word in title for word in ["security", "surge", "anomalous", "protocol", "adjustment"]):
                sentiment_score += 1
            else:
                sentiment_score -= 0.5
                
    confidence = max(10.0, min(95.0, 50.0 + (sentiment_score * 5)))
    
    print("\n--- [PREDICTION MARKET SYNTHESIS] ---")
    print(f"Evaluated Windows       : Last {len(recent_entries)} Cycles")
    print(f"Calculated Volatility   : {sentiment_score}")
    print(f"Suggested Action Bias   : {'LONG / BULLISH' if sentiment_score > 0 else 'HEDGED / DEFENSIVE'}")
    print(f"Confidence Metric       : {confidence:.2f}%")
    print("---------------------------------------\n")

if __name__ == "__main__":
    evaluate_market_signals()