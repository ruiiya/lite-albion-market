"""
Command-line interface for the Albion Online market application.
"""
import sys
import os
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_app.market_analyzer import MarketAnalyzer
from shared.filter import Filter
from shared.constants import SHORTNAME, LOCATIONS

class MarketCLI:
    """
    Command-line interface for interacting with the Albion Online market data.
    Provides commands for data analysis, filtering, and export.
    """
    
    def __init__(self):
        """Initialize the market CLI."""
        self.analyzer = MarketAnalyzer()
        self.filter = Filter()
        print("[INFO] Market Application initialized")
        print("[INFO] Using Market.db database with separate tables")
    
    def run(self):
        """Run the CLI command loop."""
        print("[INFO] Ready for commands. Type 'help' for available commands.")
        
        while True:
            try:
                # Get command from user
                command_line = input("> ").strip()
                if not command_line:
                    continue
                    
                args = command_line.split(" ")
                command = args[0].lower()
                
                # Process commands
                if command == "exit" or command == "quit":
                    break
                elif command == "help":
                    self._show_help()
                elif command == "csv":
                    self._handle_csv_command(args[1:])
                elif command == "clear":
                    self._handle_clear_command(args[1:])
                elif command == "set":
                    self._handle_set_command(args[1:])
                elif command == "bulk":
                    self._handle_bulk_command(args[1:])
                else:
                    print(f"[ERROR] Unknown command: {command}")
            
            except Exception as e:
                print(f"[ERROR] {e}")
    
    def _show_help(self):
        """Show help information."""
        print("Available commands:")
        print("  help                 - Show this help message")
        print("  csv [locations]      - Export data to CSV files")
        print("  clear [locations]    - Clear data for specified locations")
        print("  set tier [tiers]     - Set tier filter (e.g., '4.0 5.1 6.2')")
        print("  set quality [quals]  - Set quality filter (e.g., '1 2 3')")
        print("  set diff [num]       - Set minimum profit ratio (e.g., '1.3')")
        print("  bulk [locations]     - Compare black market with royal cities")
        print("  exit                 - Exit the application")
        print()
        print("Location shortcuts:")
        for short, full in SHORTNAME.items():
            print(f"  {short} - {full}")
    
    def _handle_csv_command(self, args):
        """
        Handle the CSV export command.
        
        Args:
            args: Command arguments
        """
        # Convert location shortcuts to full names
        locations = [SHORTNAME.get(loc, loc) for loc in args]
        
        # If no locations specified, use all
        if not locations:
            locations = list(set(LOCATIONS.values()))
        
        for loc in locations:
            path = self.analyzer.export_location_to_csv(loc, self.filter)
            if path:
                print(f"[INFO] Exported {loc} data to {path}")
            else:
                print(f"[INFO] No data to export for {loc}")
    
    def _handle_clear_command(self, args):
        """
        Handle the clear data command.
        
        Args:
            args: Command arguments
        """
        # Convert location shortcuts to full names
        locations = [SHORTNAME.get(loc, loc) for loc in args]
        
        # If no locations specified, use all
        if not locations:
            locations = list(set(LOCATIONS.values()))
        
        for loc in locations:
            success = self.analyzer.clear_location_data(loc)
            if success:
                print(f"[INFO] Cleared data for {loc}")
            else:
                print(f"[INFO] No data found for {loc}")
    
    def _handle_set_command(self, args):
        """
        Handle the set filter command.
        
        Args:
            args: Command arguments
        """
        if len(args) < 1:
            print("[ERROR] Missing filter type. Use 'set tier', 'set quality', or 'set diff'")
            return
            
        filter_type = args[0].lower()
        filter_values = args[1:]
        
        if filter_type == "tier":
            # Set tier filter (e.g., "4.0 5.1")
            self.filter.set_tier(" ".join(filter_values))
            print(f"[INFO] Set tier filter to: {self.filter.tiers}")
            
        elif filter_type == "quality":
            # Set quality filter (e.g., "1 2 3")
            try:
                qualities = [int(q) for q in filter_values]
                if not qualities:
                    qualities = [1, 2, 3, 4, 5]
                self.filter.set_quality(qualities)
                print(f"[INFO] Set quality filter to: {self.filter.qualities}")
            except ValueError:
                print("[ERROR] Quality values must be integers (1-5)")
                
        elif filter_type == "diff":
            # Set minimum profit ratio (e.g., "1.3")
            try:
                if filter_values:
                    diff_value = float(filter_values[0])
                    self.filter.set_diff(diff_value)
                    print(f"[INFO] Set minimum profit ratio to: {self.filter.diff_show}")
                else:
                    print(f"[INFO] Current minimum profit ratio: {self.filter.diff_show}")
            except ValueError:
                print("[ERROR] Diff value must be a number")
                
        else:
            print(f"[ERROR] Unknown filter type: {filter_type}")
    
    def _handle_bulk_command(self, args):
        """
        Handle the bulk market comparison command.
        
        Args:
            args: Command arguments
        """
        # Need at least one royal city to compare
        if not args:
            print("[ERROR] Please specify at least one royal city for comparison")
            return
            
        # Convert location shortcuts to full names
        locations = [SHORTNAME.get(loc, loc) for loc in args]
        
        # For each royal city, compare with black market
        for loc in locations:
            if loc == "BlackMarket" or loc == "bm":
                continue  # Skip direct black market comparison
                
            print(f"[INFO] Comparing {loc} with BlackMarket...")
            comparison = self.analyzer.compare_markets(loc, self.filter)
            
            if comparison.empty:
                print(f"[INFO] No comparable data between {loc} and BlackMarket")
                continue
                
            # Sort results by item name
            comparison = comparison.sort_values(by="name", ascending=False)
                
            # Quick sell comparison (royal city → black market buy order)
            df_qs = comparison[["name", "enchant", "sell_min_rl", "buy_max_bm", 
                              "diff_quick_sell", "quick_sell_desired"]]
            df_qs = df_qs[df_qs["diff_quick_sell"] > self.filter.diff_show]
            
            # Sell order comparison (royal city → black market sell order)
            df_so = comparison[["name", "enchant", "sell_min_rl", "sell_min_bm", 
                              "diff_sell_order", "sell_order_desired"]]
            df_so = df_so[df_so["diff_sell_order"] > self.filter.diff_show]
            
            # Display results
            if not df_qs.empty:
                print("\nQuick Sell Opportunities (Royal City → Black Market Buy Orders):")
                pd.set_option('display.max_rows', None)
                print(df_qs)
                
            if not df_so.empty:
                print("\nSell Order Opportunities (Royal City → Black Market Sell Orders):")
                pd.set_option('display.max_rows', None)
                print(df_so)
                
            if df_qs.empty and df_so.empty:
                print(f"[INFO] No profitable opportunities found between {loc} and BlackMarket")
    
    def close(self):
        """Close the analyzer and clean up resources."""
        if self.analyzer:
            self.analyzer.close()