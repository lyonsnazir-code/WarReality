import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds

load_dotenv()

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = os.getenv("POLY_PRIVATE_KEY")

api_creds = ApiCreds(
    api_key=os.getenv("POLY_API_KEY"),
    api_secret=os.getenv("POLY_API_SECRET"),
    api_passphrase=os.getenv("POLY_API_PASSPHRASE")
)

client = ClobClient(host=HOST, key=PRIVATE_KEY, chain_id=CHAIN_ID, creds=api_creds)

try:
    print("[INFO] Fetching account details from Polymarket CLOB...")
    # Check balances/allowances
    balances = client.get_balances()
    print(f"Balances/Collateral: {balances}")
    
    # Check open orders
    open_orders = client.get_open_orders()
    print(f"Open Orders: {open_orders}")
except Exception as e:
    print(f"[ERROR] Failed to query CLOB account: {e}")