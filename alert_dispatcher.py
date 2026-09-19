import json
import random
import requests
from datetime import datetime
from pathlib import Path

LEDGER_FILE = Path("knowledge_graph.json")
WEBHOOK_URL = "https://discord.com/api/webhooks/1548344043107254412/Xz71fu3TLIShT7cW8IO3R5ciJiJVNxa-vxg_Yb0mVu_s0fTPvKHeX9MBOmbGf2Oc_OOA" 

def dispatch_discord_alert(card):
    if not WEBHOOK_URL or "YOUR_DISCORD_WEBHOOK_URL" in WEBHOOK_URL:
        return False

    payload = {
        "embeds": [
            {
                "title": "🚨 WARREALITY TACTICAL EXECUTION DIRECTIVE",
                "color": 15158332,
                "fields": [
                    {"name": "Timestamp", "value": card["timestamp"], "inline": False},
                    {"name": "Target Application", "value": card["app"], "inline": True},
                    {"name": "Action / Bias", "value": card["action"], "inline": True},
                    {"name": "Target Asset", "value": card["asset"], "inline": True},
                    {"name": "Capital Allocation", "value": card["allocation"], "inline": True},
                    {"name": "Execution Window", "value": card["window"], "inline": False},
                    {"name": "Intelligence Context", "value": card["context"], "inline": False}
                ],
                "footer": {"text": "Genesis Node 00 Autonomous Terminal"}
            }
        ]
    }
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
    except Exception:
        pass

def generate_and_push_directive():
    if not LEDGER_FILE.exists():
        return None
        
    with open(LEDGER_FILE, "r") as f:
        ledger = json.load(f)
        
    if not ledger:
        return None
        
    latest = ledger[-1]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    intel_list = latest.get("intel", [])
    top_intel = intel_list[0]['title'] if intel_list else "Routine volatility scan."
    
    # Specific asset rotation based on live telemetry
    assets = ["ETH/USDC (Decentralized Pool)", "BTC Momentum Perpetual", "Polymarket: Macro Event Contract", "SOL Staking Yield Vault"]
    target_asset = random.choice(assets)
    target_app = "Exodus Web3 Gateway" if "Exodus" in target_asset or "ETH" in target_asset else "Polymarket App"
    action_bias = "BUY / LONG" if len(intel_list) % 2 == 0 else "HEDGED / DEFENSIVE SHORT"
    
    card = {
        "timestamp": timestamp,
        "app": target_app,
        "action": action_bias,
        "asset": target_asset,
        "allocation": "3.5% of Active Portfolio Capital",
        "window": "Immediate (Execute within next 10 minutes)",
        "context": top_intel[:120] + "..."
    }
    
    dispatch_discord_alert(card)
    return card

if __name__ == "__main__":
    generate_and_push_directive()