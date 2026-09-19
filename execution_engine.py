import os
import json
import requests
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

load_dotenv()

HOST = "https://clob.polymarket.com"
GAMMA_URL = "https://gamma-api.polymarket.com/markets"
CHAIN_ID = 137  # Polygon Mainnet

PRIVATE_KEY = os.getenv("POLY_PRIVATE_KEY")
SIGNATURE_TYPE = 1  # 1 for Email/Magic Link proxy wallets, 2 for MetaMask/Browser wallets

def get_live_token_id():
    """Fetches a guaranteed active market token ID from Polymarket's Gamma API."""
    print("[Engine] Querying Gamma API for an active market token...")
    params = {"active": "true", "closed": "false", "limit": 1, "order": "volume24hr", "ascending": "false"}
    try:
        res = requests.get(GAMMA_URL, params=params, timeout=5)
        if res.status_code == 200:
            markets = res.json()
            if markets:
                m = markets[0]
                print(f"[Market Found] {m.get('question')}")
                raw_tokens = m.get("clobTokenIds")
                tokens = json.loads(raw_tokens) if isinstance(raw_tokens, str) else raw_tokens
                if tokens and len(tokens) > 0:
                    return tokens[0] # Return the YES outcome token ID
    except Exception as e:
        print(f"[Error] Failed to fetch live market: {e}")
    return None

def initialize_authenticated_client():
    print("[Execution Engine] Initializing authenticated client connection...")
    if not PRIVATE_KEY or PRIVATE_KEY == "0x_your_actual_private_key_here":
        print("[Error] POLY_PRIVATE_KEY is not set correctly in your .env file.")
        return None

    try:
        client = ClobClient(
            host=HOST,
            key=PRIVATE_KEY,
            chain_id=CHAIN_ID,
            signature_type=SIGNATURE_TYPE,
            funder=None 
        )
        api_creds = client.create_or_derive_api_creds()
        client.set_api_creds(api_creds)
        print("[Success] Wallet authenticated and L2 API credentials derived!")
        return client
    except Exception as e:
        print(f"[Auth Error] Failed to initialize client: {e}")
        return None

def execute_limit_order(price, size, side=BUY, live_dispatch=False):
    token_id = get_live_token_id()
    if not token_id:
        print("[Error] Could not find a valid live token ID to trade.")
        return

    client = initialize_authenticated_client()
    if not client:
        return
    
    try:
        order_args = OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id,
        )
        
        print(f"[Execution Engine] Building and signing order -> Token: {token_id[:10]}... | Price: ${price} | Size: {size}")
        signed_order = client.create_order(order_args)
        
        if live_dispatch:
            response = client.post_order(signed_order, OrderType.GTC)
            print(f"[SUCCESS] Live order posted to CLOB: {response}")
        else:
            print("[Simulation Mode] Order successfully signed for a live active market! Set live_dispatch=True to broadcast live.")
            
    except Exception as e:
        print(f"[Execution Error] Order execution failed: {e}")

if __name__ == "__main__":
    print("=== LIVE-AWARE EXECUTION ENGINE ===")
    # Test order with safe simulation mode on a live token
    execute_limit_order(price=0.02, size=10.0, side=BUY, live_dispatch=False)