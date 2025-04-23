"""
Main entry point for the Albion Online market data collector.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network import photon
from collector.market_collector import MarketCollector

def main():
    """Main entry point for the data collector application."""
    print("[INFO] Starting Albion Online Market Data Collector")
    print("[INFO] Please zone to another map before start collecting data")
    print("[INFO] All data will be saved to Market.db database with separate tables per location")
    
    # Create the collector instance
    collector = MarketCollector()
    
    # Set up the photon packet handlers
    p = photon.Photon()
    p.map_request(75, collector.process_sell_orders)  # Sell order packets
    p.map_request(76, collector.process_buy_orders)   # Buy order packets
    p.map_request(2, lambda params: collector.set_player_location(params[8]))  # Location update packets
    
    print("[INFO] Collector is running. Press Enter to stop.")
    try:
        input()  # Wait for user to press Enter
    except KeyboardInterrupt:
        print("\n[INFO] Collector stopped by user")
    finally:
        collector.close()
        print("[INFO] Collector has been stopped")

if __name__ == "__main__":
    main()