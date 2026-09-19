import json, os  
LEDGER_FILE = "trade_ledger.json"  
def get_performance_summary():  
    if not os.path.exists(LEDGER_FILE): print("[STATS] No trade history found yet."); return  
    try:  
        with open(LEDGER_FILE, "r") as f: trades = json.load(f)  
    except json.JSONDecodeError: trades = []  
    total = len(trades)  
    wins = sum(1 for t in trades if t.get("win", False))  
    print(f"Total Trades: {total} | Wins: {wins}")  
if __name__ == "__main__": get_performance_summary() 
