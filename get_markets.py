import os
from polymarket_us import PolymarketUS
from dotenv import load_dotenv

load_dotenv()

client = PolymarketUS(
    key_id=os.getenv("PM_US_KEY_ID"),
    secret_key=os.getenv("PM_US_SECRET"),
)

try:
    print("[INFO] Fetching active markets...")
    markets = client.markets.list()
    print(markets)
except Exception as e:
    print(f"[ERROR] {e}")
finally:
    client.close()
