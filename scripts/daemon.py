import time
import random
from datetime import datetime
from osint_scraper import fetch_osint_headlines
from knowledge_graph import log_event
from alert_dispatcher import generate_and_push_directive
from executor import execute_autonomous_order

def run_daemon():
    print("[WARREALITY ENGINE] Node 00 Daemon Operational.")
    print("[WARREALITY ENGINE] Monitoring streams. Press Ctrl+C to stop.")
    
    try:
        tick_count = 0
        while True:
            time.sleep(2)
            tick_count += 20
            
            # Simulate anomaly detection stream
            if random.random() > 0.3:
                anomalies = [
                    round(random.uniform(120.0, 140.0), 10),
                    round(random.uniform(120.0, 140.0), 10)
                ]
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"[{timestamp}] Processed 20 ticks | Anomalies: {len(anomalies)}")
                print(f"    --> [FLAGGED ANOMALY]: {anomalies}")
                print(f"    --> [OSINT TRIGGERED] Fetching tactical intel...")
                
                # Fetch live intelligence
                headlines = fetch_osint_headlines("crypto cartel geopolitical intelligence", max_results=3)
                
                for item in headlines:
                    print(f"        [INTEL]: {item['title']}")
                
                # 1. Log safely to Knowledge Graph
                log_event(anomalies, headlines)
                
                # 2. Push directive to Discord
                generate_and_push_directive()
                
                # 3. Execute autonomous trade order via Web3 rails
                execute_autonomous_order()
                
    except KeyboardInterrupt:
        print("\n[GENESIS DAEMON] Execution halted safely.")

if __name__ == "__main__":
    run_daemon()
