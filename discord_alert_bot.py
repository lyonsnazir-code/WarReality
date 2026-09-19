import csv
import os
import time
import json
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1548438029566484641/k4fD7WSgEnAVKSV-NMxFH6h9VcU1d40QkG0NGibVS5U3EHQtecBez62FoZYMe10xezMJ"

TARGET_KEYWORDS = [
    "newsom", "trump", "biden", "harris", "election", "democrat", "republican", "senate", "house",
    "bitcoin", "btc", "ethereum", "eth", "solana", "crypto", "fed", "rate",
    "nfl", "nba", "mlb", "super bowl", "champion", "desantis", "spanberger"
]

MIN_VOLUME_USD = 1000.0        
CHECK_INTERVAL_SECONDS = 1800  
LOG_FILE = "multi_venue_history.csv"

sent_market_ids = set()

def init_csv():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Venue", "Keyword", "Question", "Odds", "Volume_USD", "Link"])

def log_alert(timestamp, venue, keyword, question, odds, volume, link):
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, venue, keyword, question, odds, volume, link])

def fetch_polymarket():
    """Scans Polymarket Gamma API."""
    print("[Radar] Querying Polymarket...")
    markets_data = []
    try:
        url = f"https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=50&volumeNumMin={MIN_VOLUME_USD}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            for m in res.json():
                q = m.get("question", "Unknown")
                slug = m.get("slug", "")
                market_id = f"poly_{m.get('id') or slug}"
                
                if market_id in sent_market_ids:
                    continue
                
                # Check keywords
                matched = next((kw for kw in TARGET_KEYWORDS if kw in q.lower()), None)
                if not matched:
                    continue
                
                vol = float(m.get("volumeNum") or m.get("volume") or 0.0)
                if vol < MIN_VOLUME_USD:
                    continue
                
                # Parse odds
                odds_text = "N/A"
                raw_prices = m.get("outcomePrices")
                if raw_prices:
                    try:
                        prices = json.loads(raw_prices) if isinstance(raw_prices, str) else raw_prices
                        if prices and len(prices) >= 2:
                            odds_text = f"YES: {float(prices[0])*100:.1f}% | NO: {float(prices[1])*100:.1f}%"
                    except Exception:
                        pass

                markets_data.append({
                    "id": market_id,
                    "venue": "Polymarket",
                    "keyword": matched,
                    "question": q,
                    "odds": odds_text,
                    "volume": vol,
                    "link": f"https://polymarket.com/market/{slug}"
                })
    except Exception as e:
        print(f"Polymarket scan error: {e}")
    return markets_data

def fetch_kalshi():
    """Scans Kalshi Public Trade API."""
    print("[Radar] Querying Kalshi...")
    markets_data = []
    try:
        # Public Kalshi markets endpoint
        url = "https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit=50"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            kalshi_markets = data.get("markets", [])
            for m in kalshi_markets:
                q = m.get("title") or m.get("subtitle") or "Unknown Kalshi Event"
                ticker = m.get("ticker", "")
                market_id = f"kalshi_{ticker}"
                
                if market_id in sent_market_ids:
                    continue
                
                matched = next((kw for kw in TARGET_KEYWORDS if kw in q.lower()), None)
                if not matched:
                    continue
                
                # Kalshi volume/liquidity tracking
                vol = float(m.get("volume") or m.get("open_interest") or 0.0)
                
                # Extract pricing from yes/no bid/ask or last price
                yes_price = m.get("yes_bid", 50) / 100.0 if m.get("yes_bid") else 0.50
                odds_text = f"Approx YES: {yes_price*100:.1f}%"

                markets_data.append({
                    "id": market_id,
                    "venue": "Kalshi",
                    "keyword": matched,
                    "question": q,
                    "odds": odds_text,
                    "volume": vol,
                    "link": "https://kalshi.com"
                })
    except Exception as e:
        print(f"Kalshi scan error: {e}")
    return markets_data

def run_scanner():
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[Multi-Venue Radar] Scan started at {now_str}")
    
    all_markets = fetch_polymarket() + fetch_kalshi()
    alerts_sent = 0

    for m in all_markets:
        market_id = m["id"]
        if market_id in sent_market_ids:
            continue
            
        msg = (
            f"🌐 **CROSS-VENUE RADAR ALERT** [{m['venue']}] (Matched: `{m['keyword']}`)\n\n"
            f"**Market:** {m['question']}\n"
            f"📊 **Odds:** {m['odds']}\n"
            f"💰 **Volume Indicator:** ${m['volume']:,.2f}\n"
            f"🔗 **Platform Link:** {m['link']}"
        )
        
        response = requests.post(WEBHOOK_URL, json={"content": msg})
        if response.status_code == 204:
            print(f"[{m['venue']}] Sent alert for: {m['question']}")
            sent_market_ids.add(market_id)
            log_alert(now_str, m["venue"], m["keyword"], m["question"], m["odds"], m["volume"], m["link"])
            alerts_sent += 1

    print(f"[Multi-Venue Radar] Complete. Dispatched {alerts_sent} cross-platform signals.")

if __name__ == "__main__":
    init_csv()
    print("=== MULTI-VENUE INTELLIGENCE ENGINE INITIALIZED ===")
    run_scanner()
    
    while True:
        try:
            time.sleep(CHECK_INTERVAL_SECONDS)
            run_scanner()
        except KeyboardInterrupt:
            print("\nRadar shut down.")
            break