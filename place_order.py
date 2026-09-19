import os
from polymarket_us import PolymarketUS
from dotenv import load_dotenv

load_dotenv()

client = PolymarketUS(
    key_id=os.getenv("PM_US_KEY_ID"),
    secret_key=os.getenv("PM_US_SECRET"),
)

try:
    print("[INFO] Fetching open orders via SDK...")
    open_orders = client.orders.list()
    print(f"[SUCCESS] Connected! Open orders: {open_orders}")
except Exception as e:
    print(f"[ERROR] {e}")
finally:
    client.close()
