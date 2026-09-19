import os
from dotenv import load_dotenv
from py_clob_client_v2.client import ClobClient
from py_clob_client_v2.clob_types import OrderArgs, OrderType
from py_clob_client_v2.order_builder.constants import BUY

load_dotenv()

print("[INFO] Initializing Polymarket V2 Deposit Wallet client...")

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
private_key = os.getenv("PK")
MY_ADDRESS = "0x0666864db732d3e04C5009e0373750cD2410498C"

# Initialize client with signature type 3 and your funder address
temp_client = ClobClient(
    host=HOST,
    key=private_key,
    chain_id=CHAIN_ID,
    signature_type=3,
    funder=MY_ADDRESS
)

print("[INFO] Deriving valid L2 API credentials directly from your private key...")
try:
    # This signs a message with your private key to securely derive your matching L2 credentials
    creds = temp_client.derive_api_key()
    temp_client.set_api_creds(creds)
    print("[SUCCESS] L2 API credentials derived and synchronized!")
except Exception as e:
    print(f"[ERROR] Failed to derive API credentials: {e}")
    exit(1)

TARGET_TOKEN_ID = "32338220190071351435772801779725302244575775216413325951443816017994629993401"

order_args = OrderArgs(
    price=0.01,
    size=5.0,
    side=BUY,
    token_id=TARGET_TOKEN_ID
)

print("[INFO] Signing and posting live order via deposit wallet...")
try:
    signed_order = temp_client.create_order(order_args)
    response = temp_client.post_order(signed_order, OrderType.GTC)
    print(f"\n[SUCCESS] Order Response Received:\n{response}")
except Exception as e:
    print(f"\n[ERROR] Order execution failed: {e}")