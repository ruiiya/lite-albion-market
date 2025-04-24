"""
Command-line interface for the Albion Online market application.
"""
import sys
import os
import pandas as pd
import logging

# Set up logging
logger = logging.getLogger(__name__)

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
        logger.info("Market Application initialized")
        logger.info("Using Market.db database with separate tables")
    
    def run(self):
        """Run the CLI command loop."""
        logger.info("Ready for commands. Type 'help' for available commands.")
        
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
                elif command == "show":
                    self._handle_show_command(args[1:])
                else:
                    logger.error(f"Unknown command: {command}")
            
            except Exception as e:
                logger.error(f"Error: {str(e)}", exc_info=True)
    
    def _show_help(self):
        """Show help information."""
        help_text = """Available commands:
  help                 - Show this help message
  csv [locations]      - Export data to CSV files
  clear [locations]    - Clear data for specified locations
  set tier [tiers]     - Set tier filter (e.g., '4.0 5.1 6.2')
  set quality [quals]  - Set quality filter (e.g., '1 2 3')
  set diff [num]       - Set minimum profit ratio (e.g., '1.3')
  bulk [locations]     - Compare black market with royal cities
  show                 - Show current filter settings
  show [locations]     - Show market data for specified locations
  show all             - Show market data for all locations
  exit                 - Exit the application

Location shortcuts:"""
        print(help_text)
        logger.debug("Help command executed")
        
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
        
        logger.info(f"CSV export requested for locations: {locations}")
        
        for loc in locations:
            path = self.analyzer.export_location_to_csv(loc, self.filter)
            if path:
                logger.info(f"Exported {loc} data to {path}")
    
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
        
        logger.info(f"Clear data requested for locations: {locations}")
        
        for loc in locations:
            success = self.analyzer.clear_location_data(loc)
    
    def _handle_set_command(self, args):
        """
        Handle the set filter command.
        
        Args:
            args: Command arguments
        """
        if len(args) < 1:
            logger.error("Missing filter type")
            return
            
        filter_type = args[0].lower()
        filter_values = args[1:]
        
        if filter_type == "tier":
            # Set tier filter (e.g., "4.0 5.1")
            self.filter.set_tier(" ".join(filter_values))
            logger.info(f"Set tier filter to: {self.filter.tiers}")
            
        elif filter_type == "quality":
            # Set quality filter (e.g., "1 2 3")
            try:
                qualities = [int(q) for q in filter_values]
                if not qualities:
                    qualities = [1, 2, 3, 4, 5]
                self.filter.set_quality(qualities)
                logger.info(f"Set quality filter to: {self.filter.qualities}")
            except ValueError:
                logger.error("Quality values must be integers (1-5)")
                
        elif filter_type == "diff":
            # Set minimum profit ratio (e.g., "1.3")
            try:
                if filter_values:
                    diff_value = float(filter_values[0])
                    self.filter.set_diff(diff_value)
                    logger.info(f"Set minimum profit ratio to: {self.filter.diff_show}")
                else:
                    logger.info(f"Current minimum profit ratio: {self.filter.diff_show}")
            except ValueError:
                logger.error("Diff value must be a number")
                
        else:
            logger.error(f"Unknown filter type: {filter_type}")
    
    def _handle_bulk_command(self, args):
        """
        Handle the bulk market comparison command.
        
        Args:
            args: Command arguments
        """
        # Need at least one royal city to compare
        if not args:
            logger.error("No royal city specified for comparison")
            return
            
        # Convert location shortcuts to full names
        locations = [SHORTNAME.get(loc, loc) for loc in args]
        logger.info(f"Bulk comparison requested for locations: {locations}")
        
        # For each royal city, compare with black market
        for loc in locations:
            if loc == "BlackMarket" or loc == "bm":
                continue  # Skip direct black market comparison
                
            logger.info(f"Comparing {loc} with BlackMarket...")
            comparison = self.analyzer.compare_markets(loc, self.filter)
            
            if comparison.empty:
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
                logger.info(f"Found {len(df_qs)} quick sell opportunities for {loc}")
                print("\nQuick Sell Opportunities (Royal City → Black Market Buy Orders):")
                pd.set_option('display.max_rows', None)
                print(df_qs)
                
            if not df_so.empty:
                logger.info(f"Found {len(df_so)} sell order opportunities for {loc}")
                print("\nSell Order Opportunities (Royal City → Black Market Sell Orders):")
                pd.set_option('display.max_rows', None)
                print(df_so)

    def _handle_show_command(self, args):
        """

        Handle the show command for displaying market data.
        
        Args:
            args: Command arguments
        """
        if len(args) < 1:
            # show current filter settings
            print(f"Current filter settings:\n"
                  f"    Tier: {self.filter.get_tier()}\n"
                  f"    Quality: {self.filter.get_quality()}\n"
                  f"    Minimum Price Difference: {self.filter.get_diff()}")
            return
        
        if args[0].lower() == "all":
            # Show data for all locations
            logger.info("Showing data for all locations")
            # Show data for all locations
            locations = list(set(LOCATIONS.values()))  # Use set to remove duplicates
            for loc in locations:
                df = self.analyzer.get_location_data(loc, self.filter)
                if df.empty:
                    continue
                
                # Display the data
                print(f"\nData for {loc}:")
                print(df)
        else:
            for loc in args:
                loc = SHORTNAME.get(loc, loc)
                
                # Get data for the specified location
                df = self.analyzer.get_location_data(loc, self.filter)
                
                if df.empty:
                    continue
                
                # Display the data
                print(f"\nData for {loc}:")
                print(df)


    def close(self):
        """Close the analyzer and clean up resources."""
        logger.info("Closing CLI resources")
        if self.analyzer:
            self.analyzer.close()