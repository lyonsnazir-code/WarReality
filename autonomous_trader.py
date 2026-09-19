import datetime
from zoneinfo import ZoneInfo
import time

class InstitutionalRiskEngine:
    def __init__(self, max_spread=0.03, min_depth_total=50.0, risk_percentage=0.10):
        self.max_spread = max_spread  # Maximum allowable bid-ask spread
        self.min_depth_total = min_depth_total  # Minimum combined liquidity pool
        self.risk_percentage = risk_percentage  # Fraction of capital to risk per trade (e.g., 10%)
        self.ny_tz = ZoneInfo("America/New_York")

    def validate_ict_session(self) -> bool:
        """
        ICT Session Filter: Restricts trading to high-probability institutional windows.
        """
        now_ny = datetime.datetime.now(self.ny_tz)
        current_hour = now_ny.hour
        current_minute = now_ny.minute
        is_core_session = (8 <= current_hour < 16) or (current_hour == 16 and current_minute <= 30)
        return is_core_session

    def evaluate_order_parameters(self, bid: float, ask: float, total_depth: float, imbalance_ratio: float, current_balance: float) -> tuple[bool, float]:
        """
        Evaluates spread, depth, and scales position size dynamically based on current wallet balance.
        """
        spread = round(ask - bid, 4)

        # 1. Spread Check: Reject if book is too gappy
        if spread > self.max_spread:
            return False, 0.0

        # 2. Depth Check: Reject if liquidity is too thin
        if total_depth < self.min_depth_total:
            return False, 0.0

        # 3. Dynamic Position Sizing (e.g., 10% of $70 = $7.00 base size)
        calculated_size = current_balance * self.risk_percentage

        # 4. Confidence Multiplier for High Imbalance
        if imbalance_ratio > 0.85:
            calculated_size *= 1.25  # Scale up slightly for high-conviction order flow

        # Ensure order size respects minimum limits and doesn't exceed balance
        adjusted_size = round(max(1.0, min(calculated_size, current_balance)), 2)

        return True, adjusted_size

if __name__ == "__main__":
    print("Genesis Node: Institutional Risk Engine initialized. Starting continuous market scan loop...")
    engine = InstitutionalRiskEngine()
    
    while True:
        session_active = engine.validate_ict_session()
        print(f"[{datetime.datetime.now()}] Scanning market spreads... ICT Session Active: {session_active}")
        # Add your live orderbook fetching and arbitrage execution hooks here
        time.sleep(30)