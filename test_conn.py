import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds

# Load variables from .env file
load_dotenv()

host = "https://clob.polymarket.com"
chain_id = 137

# 1. Initialize the base client with your wallet private key
client = ClobClient(
    host=host,
    key=os.getenv("PK"), # Ensure your private key variable in .env is named PK or change this to match
    chain_id=chain_id
)

# 2. Inject your L2 API credentials explicitly using ApiCreds
creds = ApiCreds(
    api_key=os.getenv("POLYMARKET_API_KEY"),
    api_secret=os.getenv("POLYMARKET_SECRET"),
    api_passphrase=os.getenv("POLYMARKET_PASSPHRASE")
)
client.set_api_creds(creds)

print("[INFO] Testing connection to Polymarket...")
try:
    server_time = client.get_server_time()
    print(f"[SUCCESS] Connected! Polymarket Server Time: {server_time}")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")