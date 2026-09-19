import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
LEDGER_FILE = "trading_journal.json"  # Hardcoded to match your active file

def get_ledger_stats():
    """Reads journal and computes aggregate portfolio stats."""
    if not os.path.exists(LEDGER_FILE):
        return {"total_trades": 0, "net_pnl": 0.0, "total_deployed": 0.0}
    
    try:
        with open(LEDGER_FILE, "r") as f:
            trades = json.load(f)
    except:
        trades = []
        
    total_trades = len(trades)
    net_pnl = sum(t.get("pnl_usdc", 0.0) for t in trades)
    total_deployed = sum(t.get("size_usdc", 0.0) for t in trades)
    return {
        "total_trades": total_trades,
        "net_pnl": net_pnl,
        "total_deployed": total_deployed
    }

def record_and_notify_trade(market_id, side, size_usdc, entry_price, exit_price, pnl_usdc):
    """Records trade to trading_journal.json and pushes a rich Discord embed notification."""
    trade_entry = {
        "market_id": market_id,
        "side": side,
        "size_usdc": size_usdc,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "pnl_usdc": pnl_usdc
    }
    
    # Load and update journal
    trades = []
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, "r") as f:
                trades = json.load(f)
        except:
            trades = []
            
    trades.append(trade_entry)
    with open(LEDGER_FILE, "w") as f:
        json.dump(trades, f, indent=4)
        
    stats = get_ledger_stats()
    roi = (stats["net_pnl"] / 100.0) * 100 if stats["total_trades"] > 0 else 0.0

    # Build Rich Discord Embed Payload
    if DISCORD_WEBHOOK_URL:
        embed = {
            "title": "⚡ GENESIS NODE: ARBITRAGE EXECUTED",
            "color": 5763719,  # Vibrant Green
            "fields": [
                {"name": "Asset / Side", "value": f"`{side}`", "inline": True},
                {"name": "Position Size", "value": f"`${size_usdc:.2f} USDC`", "inline": True},
                {"name": "Entry Price", "value": f"`${entry_price:.2f}`", "inline": True},
                {"name": "Expected PnL", "value": f"`+${pnl_usdc:.2f} USDC`", "inline": True},
                {"name": "Condition ID", "value": f"`{market_id[:16]}...`", "inline": False},
                {"name": "📊 Cumulative Portfolio", "value": f"Total Trades: **{stats['total_trades']}** | Net PnL: **+${stats['net_pnl']:.2f} USDC** | ROI: **+{roi:.1f}%**", "inline": False}
            ],
            "footer": {"text": "Genesis Node Autonomous Protocol • Live Production"}
        }
        
        try:
            requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=5)
        except Exception as e:
            print(f"[DISCORD ERROR] Failed to dispatch webhook embed: {e}")