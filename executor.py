import time
import os
import json
import requests
from dotenv import load_dotenv
from logger import record_and_notify_trade
from pnl_monitor import analyze_system_benefit, get_cumulative_pnl

# Import Polymarket CLOB Client & Dependencies
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
from py_clob_client.order_builder.constants import BUY

load_dotenv()
GAMMA_URL = "https://gamma-api.polymarket.com/markets"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Initialize Real CLOB Client using your existing .env keys
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = os.getenv("POLY_PRIVATE_KEY")

api_creds = ApiCreds(
    api_key=os.getenv("POLY_API_KEY"),
    api_secret=os.getenv("POLY_API_SECRET"),
    api_passphrase=os.getenv("POLY_API_PASSPHRASE")
)

clob_client = None
if PRIVATE_KEY:
    try:
        clob_client = ClobClient(
            host=HOST,
            key=PRIVATE_KEY,
            chain_id=CHAIN_ID,
            creds=api_creds
        )
        print("[INIT] Py-Clob-Client authenticated and ready for live execution.")
    except Exception as e:
        print(f"[CLOB INIT ERROR] Failed to initialize client: {e}")

session = requests.Session()
BASE_POSITION_USDC = 10.0
MIN_24H_VOLUME = 500_000.0

def get_dynamic_position_size():
    """Dynamically scales position size based on accumulated PnL growth."""
    try:
        current_pnl = get_cumulative_pnl()
    except:
        current_pnl = 0.0
    
    dynamic_size = BASE_POSITION_USDC + (max(0.0, current_pnl) * 0.10)
    return round(min(dynamic_size, 50.0), 2)  # Capped at $50 max per trade

def test_discord_connection():
    """Pings Discord on startup to verify webhook connectivity."""
    if DISCORD_WEBHOOK_URL:
        try:
            payload = {
                "content": "🟢 **Genesis Node Online:** Live market sweepers active. Monitoring Polymarket order books..."
            }
            requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
            print("[DISCORD] Startup heartbeat ping sent successfully.")
        except Exception as e:
            print(f"[DISCORD TEST ERROR] Failed to send startup ping: {e}")

def fetch_live_market_data():
    """Sweeps multiple Polymarket categories for high-alpha arbitrage targets."""
    all_markets = []
    endpoints = [
        {"active": "true", "closed": "false", "limit": 25, "order": "volume24hr", "ascending": "false"},
        {"active": "true", "closed": "false", "limit": 15, "order": "liquidity", "ascending": "false"},
        {"active": "true", "closed": "false", "tag": "crypto", "limit": 10, "order": "volume24hr", "ascending": "false"},
        {"active": "true", "closed": "false", "tag": "pop-culture", "limit": 10, "order": "volume24hr", "ascending": "false"}
    ]
    
    seen_ids = set()
    for params in endpoints:
        retries = 3
        backoff = 2
        for attempt in range(retries):
            try:
                response = session.get(GAMMA_URL, params=params, timeout=5)
                if response.status_code == 429:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                
                response.raise_for_status()
                for m in response.json():
                    cid = m.get("conditionId")
                    if cid and cid not in seen_ids:
                        seen_ids.add(cid)
                        all_markets.append(m)
                break
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    print(f"[API WARNING] Sweep error on {params}: {e}")
                    
    return all_markets

def parse_market_tokens(market):
    """Extracts outcomes, prices, and real CLOB token IDs from Polymarket API structures."""
    parsed_tokens = []
    tokens_data = market.get("tokens", [])
    if tokens_data:
        for token in tokens_data:
            parsed_tokens.append({
                "outcome": token.get("outcome", "Unknown"),
                "token_id": token.get("token_id", ""),
                "price": float(token.get("price", 0.0) or 0.0)
            })
        return parsed_tokens

    outcomes = market.get("outcomes", [])
    prices = market.get("outcomePrices", [])
    clob_ids = market.get("clobTokenIds", [])
    
    if isinstance(outcomes, str):
        try: outcomes = json.loads(outcomes)
        except: outcomes = []
    if isinstance(prices, str):
        try: prices = json.loads(prices)
        except: prices = []
    if isinstance(clob_ids, str):
        try: clob_ids = json.loads(clob_ids)
        except: clob_ids = []
            
    for i, outcome in enumerate(outcomes):
        price = float(prices[i]) if i < len(prices) else 0.0
        token_id = clob_ids[i] if i < len(clob_ids) else ""
        parsed_tokens.append({
            "outcome": outcome,
            "token_id": token_id,
            "price": price
        })
    return parsed_tokens

def evaluate_and_execute(market):
    """Evaluates market mispricing and logs scanned prices for debugging."""
    question = market.get("question", "Unknown Market")
    condition_id = market.get("conditionId", "0x0")
    volume = float(market.get("volume24hr", 0) or 0)
    
    if volume < MIN_24H_VOLUME:
        return
    
    tokens = parse_market_tokens(market)
    
    for t in tokens:
        price = float(t.get('price', 0.0) or 0.0)
        token_id = t.get('token_id', '')
        outcome = t.get('outcome', 'Unknown')
        
        # Debug log to see what prices are being evaluated
        print(f"[SCAN] {question[:30]}... | {outcome}: ${price:.2f} | ID: {token_id[:10]}...")
        
        # Target mispriced threshold
        if 0.01 < price <= 0.35 and token_id:
            current_position_size = get_dynamic_position_size()
            print(f"   [SIGNAL MATCH] Outcome '{outcome}' at ${price:.2f} meets target threshold!")
            print(f"[LIVE ORDER] Dispatching real order: ${current_position_size} USDC on token ID: {token_id[:12]}...")
            
            if clob_client:
                try:
                    shares_quantity = current_position_size / price
                    
                    order_args = OrderArgs(
                        price=price,
                        size=shares_quantity,
                        side=BUY,
                        token_id=token_id
                    )
                    signed_order = clob_client.create_order(order_args)
                    resp = clob_client.post_order(signed_order)
                    print(f"[CLOB SUCCESS] Order posted: {resp}")
                    
                    record_and_notify_trade(
                        market_id=condition_id,
                        side=outcome,
                        size_usdc=current_position_size,
                        entry_price=price,
                        exit_price=0.60,
                        pnl_usdc=0.0
                    )
                except Exception as e:
                    print(f"[ORDER FAILED] CLOB execution error: {e}")
            else:
                print("[CONFIG ERROR] CLOB Client not authenticated. Check .env credentials.")
            break

def run_production_loop():
    test_discord_connection()
    print("[INFO] Genesis Node LIVE Production Architecture Initialized (Real CLOB Execution Active)...")
    while True:
        try:
            markets = fetch_live_market_data()
            for market in markets:
                evaluate_and_execute(market)
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n[INFO] Manual shutdown initiated.")
            break
        except Exception as e:
            print(f"[CRITICAL ERROR] Loop exception caught: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_production_loop()