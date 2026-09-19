import os
from polymarket_us import PolymarketUS
from dotenv import load_dotenv

load_dotenv()

key_id = os.getenv("PM_US_KEY_ID")
secret_key = os.getenv("PM_US_SECRET")

print("[INFO] Initializing official PolymarketUS client...")
client = PolymarketUS(
    key_id=key_id,
    secret_key=secret_key,
)

try:
    print("[INFO] Fetching account balances...")
    balances = client.account.balances()
    print("[SUCCESS] Connected and authenticated successfully!")
    print(balances)
except Exception as e:
    print(f"[ERROR] API call failed: {e}")
finally:
    client.close()
