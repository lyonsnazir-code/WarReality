import os
from polymarket_us import PolymarketUS
from dotenv import load_dotenv

load_dotenv()

client = PolymarketUS(
    key_id=os.getenv("PM_US_KEY_ID"),
    secret_key=os.getenv("PM_US_SECRET"),
)

try:
    print("[INFO] Submitting test order to Polymarket US...")
    # Replace with a real active market slug and parameters when ready
    order = client.orders.create({
        "marketSlug": "test-market",
        "intent": "ORDER_INTENT_BUY_LONG",
        "type": "ORDER_TYPE_LIMIT",
        "price": {"value": "0.10", "currency": "USD"},
        "quantity": 1,
        "tif": "TIME_IN_FORCE_GOOD_TILL_CANCEL",
    })
    print(f"[SUCCESS] Order response: {order}")
except Exception as e:
    print(f"[ERROR] Order submission note: {e}")
finally:
    client.close()
