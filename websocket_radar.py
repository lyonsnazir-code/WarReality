import asyncio
import json
import websockets

# Polymarket CLOB Market WebSocket Endpoint
WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

async def subscribe_market(token_ids):
    async with websockets.connect(WS_URL) as ws:
        sub_payload = {
            "assets_ids": token_ids,
            "type": "market"
        }
        await ws.send(json.dumps(sub_payload))
        print(f"Subscribed to asset IDs: {token_ids}")

        asyncio.create_task(heartbeat(ws))

        try:
            async for message in ws:
                data = json.loads(message)
                # Handle both single dictionary messages or lists of messages
                if isinstance(data, list):
                    for item in data:
                        handle_event(item)
                else:
                    handle_event(data)
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")

async def heartbeat(ws):
    while True:
        await asyncio.sleep(10)
        try:
            await ws.ping()
        except Exception:
            break

def handle_event(data):
    if not isinstance(data, dict):
        return
        
    event_type = data.get("event_type")
    
    if event_type == "price_change":
        for change in data.get("price_changes", []):
            print(f"[PRICE UPDATE] Asset: {change.get('asset_id')} | Side: {change.get('side')} | Price: {change.get('price')} | Size: {change.get('size')}")
    
    elif event_type == "last_trade_price":
        print(f"[TRADE] Asset: {data.get('asset_id')} | Price: {data.get('price')} | Size: {data.get('size')}")
        
    elif event_type == "book":
        print(f"[BOOK SNAPSHOT] Asset: {data.get('asset_id')} | Levels loaded.")
        
    elif event_type == "tick_size_change":
        print(f"[CONFIG] Tick size updated for market.")
        
    else:
        # Print raw event type for debugging incoming market data streams
        if event_type:
            print(f"[EVENT] Received type: {event_type}")

if __name__ == "__main__":
    # Example token ID
    SAMPLE_TOKEN_IDS = ["17538918577045757318"]
    print("=== STARTING ROBUST WEBSOCKET STREAM ==Renderer Online ===")
    asyncio.run(subscribe_market(SAMPLE_TOKEN_IDS))