import subprocess
import sys

def main():
    while True:
        print("\n=== [WARREALITY NODE 00 OPERATIONS CONSOLE] ===")
        print("1. Launch Real-Time Daemon (scripts.daemon)")
        print("2. Run Historical Backtest (backtester.py)")
        print("3. Evaluate Market Signals (predictor.py)")
        print("4. Exit Operations Console")
        
        choice = input("\nSelect operation mode [1-4]: ").strip()
        
        if choice == "1":
            print("\n[LAUNCHING] Starting real-time telemetry stream...\n")
            try:
                subprocess.run([sys.executable, "-m", "scripts.daemon"])
            except KeyboardInterrupt:
                print("\n[CONSOLE] Daemon halted by user. Returning to menu...")
        elif choice == "2":
            print("\n[LAUNCHING] Running historical backtest...\n")
            subprocess.run([sys.executable, "backtester.py"])
        elif choice == "3":
            print("\n[LAUNCHING] Evaluating prediction market signals...\n")
            subprocess.run([sys.executable, "predictor.py"])
        elif choice == "4":
            print("[CONSOLE] Terminating operations session. Goodbye.")
            break
        else:
            print("[ERROR] Invalid selection. Choose a number between 1 and 4.")

if __name__ == "__main__":
    main()