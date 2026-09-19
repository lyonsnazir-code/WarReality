import json
import requests

GAMMA_URL = "https://gamma-api.polymarket.com/markets"
CLOB_URL = "https://clob.polymarket.com"

def fetch_market_metadata(limit=5):
    """Discovers active markets and maps outcome token IDs using Gamma API."""
    print(f"[Ingestor] Querying Gamma API for top active markets...")
    params = {
        "active": "true",
        "closed": "false",
        "limit": limit,
        "order": "volume24hr",
        "ascending": "false"
    }
    
    response = requests.get(GAMMA_URL, params=params, timeout=10)
    if response.status_code != 200:
        print(f"Gamma API Error: {response.status_code}")
        return []
    
    markets = response.json()
    parsed_markets = []
    
    for m in markets:
        question = m.get("question", "Unknown")
        slug = m.get("slug", "")
        
        # Gamma stores token IDs and prices as JSON strings or arrays
        raw_tokens = m.get("clobTokenIds")
        raw_prices = m.get("outcomePrices")
        
        try:
            tokens = json.loads(raw_tokens) if isinstance(raw_tokens, str) else raw_tokens
            prices = json.loads(raw_prices) if isinstance(raw_prices, str) else raw_prices
        except Exception:
            tokens, prices = [], []
            
        parsed_markets.append({
            "question": question,
            "slug": slug,
            "tokens": tokens,
            "prices": prices,
            "volume_24hr": float(m.get("volume24hr") or 0.0)
        })
        
    return parsed_markets

def fetch_order_book(token_id):
    """Pulls Level 0 public order book depth for a specific outcome token from the CLOB API."""
    endpoint = f"{CLOB_URL}/book"
    params = {"token_id": token_id}
    try:
        response = requests.get(endpoint, params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"CLOB Book Fetch Error: {e}")
    return None

if __name__ == "__main__":
    print("=== INITIALIZING INFRASTRUCTURE & DATA INGESTION ===")
    active_markets = fetch_market_metadata(limit=3)
    
    for i, market in enumerate(active_markets, 1):
        print(f"\n[{i}] {market['question']}")
        print(f"    Volume (24h): ${market['volume_24hr']:,.2f}")
        print(f"    Slug: {market['slug']}")
        
        if market['tokens'] and len(market['tokens']) > 0:
            yes_token = market['tokens'][0]
            print(f"    YES Token ID: {yes_token[:20]}...")
            
            # Inspect order book depth for the YES token
            book = fetch_order_book(yes_token)
            if book:
                bids = book.get("bids", [])
                asks = book.get("asks", [])
                best_bid = bids[0] if bids else {"price": "N/A", "size": "N/A"}
                best_ask = asks[0] if asks else {"price": "N/A", "size": "N/A"}
                print(f"    📊 Order Book Top -> Best Bid: {best_bid.get('price')} (Size: {best_bid.get('size')}) | Best Ask: {best_ask.get('price')} (Size: {best_ask.get('size')})")
        print("-" * 50)