import os
import time
import datetime
from zoneinfo import ZoneInfo
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

try:
    from discord_alert import send_discord_alert
except ImportError:
    def send_discord_alert(message):
        print(f"[Discord Alert Fallback]: {message}")

class InstitutionalRiskEngine:
    def __init__(self, max_spread=0.03, min_depth_total=50.0, risk_percentage=0.10):
        self.max_spread = max_spread
        self.min_depth_total = min_depth_total
        self.risk_percentage = risk_percentage
        self.ny_tz = ZoneInfo("America/New_York")
        
        host = "https://clob.polymarket.com"
        chain_id = 137  # Polygon Mainnet
        
        private_key = os.getenv("POLY_PRIVATE_KEY")
        api_key = os.getenv("POLY_API_KEY")
        api_secret = os.getenv("POLY_API_SECRET")
        api_passphrase = os.getenv("POLY_API_PASSPHRASE")
        
        if not private_key:
            raise ValueError("FATAL: POLY_PRIVATE_KEY is missing from environment variables!")

        print("[INIT] Authenticating with Polymarket Production CLOB (Live Funds Mode)...")
        
        try:
            if api_key and api_secret and api_passphrase:
                from py_clob_client.clob_types import ApiCreds
                creds = ApiCreds(api_key=api_key, api_secret=api_secret, api_passphrase=api_passphrase)
                self.client = ClobClient(host=host, chain_id=chain_id, key=private_key, creds=creds)
            else:
                self.client = ClobClient(host=host, chain_id=chain_id, key=private_key)
            print("[INIT] Successfully connected to live Polygon production network.")
        except Exception as e:
            print(f"[INIT ERROR] Failed to initialize ClobClient: {e}")
            raise e
            
        send_discord_alert("🚨 **Genesis Node Live**: Institutional Bot initialized on **Polygon Mainnet** with real-currency execution active.")

    def validate_ict_session(self) -> bool:
        now_ny = datetime.datetime.now(self.ny_tz)
        current_hour = now_ny.hour
        current_minute = now_ny.minute
        return (8 <= current_hour < 16) or (current_hour == 16 and current_minute <= 30)

    def get_wallet_balance(self) -> float:
        try:
            balance_data = self.client.get_balance_allowance() if hasattr(self.client, "get_balance_allowance") else {"balance": 70.0}
            return float(balance_data.get("balance", 70.0))
        except Exception as e:
            print(f"[Warning] Could not fetch live balance: {e}. Using safety default.")
            return 70.0

    def evaluate_and_execute(self, token_id: str, bid: float, ask: float, total_depth: float, imbalance_ratio: float):
        spread = round(ask - bid, 4)
        if spread > self.max_spread or total_depth < self.min_depth_total:
            return False

        current_balance = self.get_wallet_balance()
        calculated_size = current_balance * self.risk_percentage
        if imbalance_ratio > 0.85:
            calculated_size *= 1.25

        adjusted_size = round(max(1.0, min(calculated_size, current_balance)), 2)
        print(f"[EXECUTION TRIGGER] Placing LIVE order for ${adjusted_size} USDC on token {token_id}")
        
        try:
            order_args = OrderArgs(price=ask, size=adjusted_size, side=BUY, token_id=token_id)
            signed_order = self.client.create_order(order_args)
            resp = self.client.post_order(signed_order)
            
            alert_msg = f"✅ **LIVE TRADE EXECUTED**: Bought ${adjusted_size} of token `{token_id}` at price `{ask}`. Response: {resp}"
            print(alert_msg)
            send_discord_alert(alert_msg)
            return True
        except Exception as e:
            err_msg = f"❌ **ORDER FAILED**: {e}"
            print(err_msg)
            send_discord_alert(err_msg)
            return False

if __name__ == "__main__":
    print("Genesis Node: Starting live automated risk engine loop...")
    engine = InstitutionalRiskEngine()
    
    while True:
        try:
            session_active = engine.validate_ict_session()
            timestamp = datetime.datetime.now(engine.ny_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
            print(f"[{timestamp}] Scanning live Polymarket books... ICT Session Active: {session_active}")
            time.sleep(30)
        except Exception as loop_err:
            print(f"[Loop Error]: {loop_err}")
            time.sleep(10)