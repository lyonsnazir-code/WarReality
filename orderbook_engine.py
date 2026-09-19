import asyncio
import json
import websockets

WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

class OrderBookManager:
    def __init__(self):
        # Maps token_id -> {"bids": {price: size}, "asks": {price: size}}
        self.books = {}

    def update_book(self, asset_id, bids, asks):
        if asset_id not in self.books:
            self.books[asset_id] = {"bids": {}, "asks": {}}
        
        # Populate snapshot or updates
        for b in bids:
            price = float(b.get("price", 0))
            size = float(b.get("size", 0))
            if size == 0:
                self.books[asset_id]["bids"].pop(price, None)
            else:
                self.books[asset_id]["bids"][price] = size
                
        for a in asks:
            price = float(a.get("price", 0))
            size = float(a.get("size", 0))
            if size == 0:
                self.books[asset_id]["asks"].pop(price, None)
            else:
                self.books[asset_id]["asks"][price] = size

    def get_best_prices(self, asset_id):
        book = self.books.get(asset_id)
        if not book or not book["bids"] or not book["asks"]:
            return None, None
            
        best_bid = max(book["bids"].keys())
        best_ask = min(book["asks"].keys())
        return best_bid, best_ask

async def monitor_market(token_ids):
    manager = OrderBookManager()
    
    async with websockets.connect(WS_URL) as ws:
        sub_payload = {"assets_ids": token_ids, "type": "market"}
        await ws.send(json.dumps(sub_payload))
        print(f"[Engine] Connected & tracking books for: {token_ids}")

        async for message in ws:
            data = json.loads(message)
            messages = data if isinstance(data, list) else [data]
            
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                    
                event_type = msg.get("event_type")
                asset_id = msg.get("asset_id")
                
                if event_type == "book":
                    manager.update_book(
                        asset_id, 
                        msg.get("bids", []), 
                        msg.get("asks", [])
                    )
                    best_bid, best_ask = manager.get_best_prices(asset_id)
                    if best_bid and best_ask:
                        spread = best_ask - best_bid
                        print(f"[BOOK UPDATE] Asset: {asset_id[:10]}... | Best Bid: ${best_bid:.2f} | Best Ask: ${best_ask:.2f} | Spread: ${spread:.2f}")
                
                elif event_type == "price_change":
                    # Handle delta changes on the book
                    for change in msg.get("price_changes", []):
                        p = float(change.get("price", 0))
                        s = float(change.get("size", 0))
                        side = change.get("side")
                        # Real-time state adjustment can be layered here

if __name__ == "__main__":
    TARGET_TOKENS = ["17538918577045757318"]
    print("=== INITIALIZING ORDER BOOK ENGINE ===")
    asyncio.run(monitor_market(TARGET_TOKENS))