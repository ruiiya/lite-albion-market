"""
Market analyzer component for analyzing Albion Online market data.
"""
import sys
import os
import pandas as pd
import numpy as np
import logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pd.set_option("future.no_silent_downcasting", True)

from shared.database import MarketDatabase
from shared.filter import Filter, regex_filter
from shared.constants import MARKET_TAX, SETUP_FEE, TOTAL_FEE

class MarketAnalyzer:
    """
    Handles the analysis of market data for the Albion Online market application.
    Provides functionality to compare markets, export data, and clear data.
    """
    
    def __init__(self):
        """Initialize the market analyzer."""
        logger.info("Initializing MarketAnalyzer")
        self.db = MarketDatabase()
        self.items_info = pd.read_csv("shared/items.csv")
        logger.debug(f"Loaded {len(self.items_info)} items from items.csv")
    
    def export_location_to_csv(self, location, filter_obj=None):
        """
        Export market data for a location to CSV file.
        
        Args:
            location: The location name (e.g., "BlackMarket")
            filter_obj: Optional Filter object to filter the data
            
        Returns:
            Path to the created CSV file or None if no data
        """
        logger.info(f"Exporting market data for {location} to CSV")
        result = self.db.export_to_csv(location, filter_obj)
        return result
    
    def clear_location_data(self, location):
        """
        Clear market data for a location.
        
        Args:
            location: The location name (e.g., "BlackMarket")
            
        Returns:
            True if successful, False otherwise
        """
        result = self.db.delete_location_data(location)
        return result
    
    def _prepare_black_market_data(self, filter_obj):
        """
        Prepare Black Market data for comparison.
        
        Args:
            filter_obj: Filter object to filter the data
            
        Returns:
            DataFrame containing filtered Black Market data
        """
        logger.debug("Preparing Black Market data")
        df = self.db.get_location_data("BlackMarket", filter_obj)
        
        if df.empty:
            logger.warning("No Black Market data found")
            return pd.DataFrame()
            
        # Group by item ID to get minimum sell price and maximum buy price
        sell = df.groupby("id")["sell_min"].min().to_frame()
        buy = df.groupby("id")["buy_max"].max().to_frame()
        
        # Merge grouped data with original data to keep enchantment level
        df = sell.merge(df[["id", "enchant", "sell_min", "buy_max"]], 
                       on="id", 
                       suffixes=("", "_y")).drop("sell_min_y", axis=1).drop_duplicates()
                       
        df = buy.merge(df[["id", "enchant", "sell_min", "buy_max"]], 
                      on="id", 
                      suffixes=("", "_y")).drop("buy_max_y", axis=1).drop_duplicates()
        
        logger.debug(f"Prepared {len(df)} Black Market items")
        return df
    
    def _prepare_royal_city_data(self, location, filter_obj):
        """
        Prepare Royal City data for comparison.
        
        Args:
            location: The location name (e.g., "Lymhurst")
            filter_obj: Filter object to filter the data
            
        Returns:
            DataFrame containing filtered Royal City data
        """
        logger.debug(f"Preparing {location} data")
        df = self.db.get_location_data(location, filter_obj)
        
        if df.empty:
            logger.warning(f"No data found for {location}")
            return pd.DataFrame()
            
        # Group by item ID to get average sell price and buy price
        sell = df.groupby("id")["sell_min"].min().to_frame()
        buy = df.groupby("id")["buy_max"].max().to_frame()
        
        # Merge grouped data with original data to keep enchantment level
        df = sell.merge(df[["id", "enchant", "sell_min", "buy_max"]], 
                       on="id", 
                       suffixes=("", "_y")).drop("sell_min_y", axis=1).drop_duplicates()
                       
        df = buy.merge(df[["id", "enchant", "sell_min", "buy_max"]], 
                      on="id", 
                      suffixes=("", "_y")).drop("buy_max_y", axis=1).drop_duplicates()
        
        logger.debug(f"Prepared {len(df)} {location} items")
        return df
    
    def compare_markets(self, royal_city, filter_obj):
        """
        Compare a royal city market with the black market.
        
        Args:
            royal_city: The royal city name (e.g., "Lymhurst")
            filter_obj: Filter object to filter the data
            
        Returns:
            DataFrame containing market comparison results
        """
        
        # Prepare data for both markets
        bm_df = self._prepare_black_market_data(filter_obj)
        royal_df = self._prepare_royal_city_data(royal_city, filter_obj)
        
        if bm_df.empty or royal_df.empty:
            logger.warning("Cannot compare markets: One or both markets have no data")
            return pd.DataFrame()
        
        # Merge data from both markets
        merge = royal_df.merge(bm_df, 
                               how="left", 
                               on=["id", "enchant"], 
                               suffixes=("_rl", "_bm")).drop_duplicates()
        
        logger.debug(f"Merged data contains {len(merge)} items")
        
        # Calculate profit metrics
        merge["diff_quick_sell"] = (merge["buy_max_bm"] * (1 - MARKET_TAX)) / merge["sell_min_rl"]
        merge["diff_sell_order"] = (merge["sell_min_bm"] * (1 - TOTAL_FEE)) / merge["sell_min_rl"]
        
        # Calculate desired buy prices based on minimum profit ratio
        merge["quick_sell_desired"] = merge["buy_max_bm"] / (filter_obj.diff_show) * (1 - MARKET_TAX)
        merge["quick_sell_desired"] = merge["quick_sell_desired"].fillna(0).infer_objects(copy=False).astype(np.int64, errors='ignore')
        
        merge["sell_order_desired"] = merge["sell_min_bm"] / (filter_obj.diff_show) * (1 - TOTAL_FEE)
        merge["sell_order_desired"] = merge["sell_order_desired"].fillna(0).infer_objects(copy=False).astype(np.int64, errors='ignore')
        
        # Convert prices to integers
        merge[["sell_min_rl", "sell_min_bm", "buy_max_bm"]] = merge[["sell_min_rl", "sell_min_bm", "buy_max_bm"]].fillna(0)
        merge[["sell_min_rl", "sell_min_bm", "buy_max_bm"]] = merge[["sell_min_rl", "sell_min_bm", "buy_max_bm"]].infer_objects(copy=False).astype(np.int64, errors='ignore')
        
        # Filter out rows with missing profit metrics
        merge = merge[merge[["diff_sell_order", "diff_quick_sell"]].notna().any(axis=1)]
        logger.debug(f"After filtering, data contains {len(merge)} profitable items")
        
        # Add item names from item info
        merge = self.items_info.merge(merge, how="right", on="id")
        logger.info(f"Market comparison completed with {len(merge)} items")

        # Sort results by item name
        merge = merge.sort_values(by="id")
        
        return merge
    
    def get_location_data(self, location, filter_obj=None):
        """
        Get market data for a specific location with optional filtering.
        
        Args:
            location: The location name (e.g., "BlackMarket")
            filter_obj: Optional Filter object to filter the data
            
        Returns:
            DataFrame containing the filtered data
        """
        logger.info(f"Getting market data for {location}")
        df = self.db.get_location_data(location, filter_obj)
        
        if df.empty:
            logger.warning(f"No data found for {location}")
            return pd.DataFrame()
            
        # Sort results by item name and quality
        df = df.sort_values(by=["id", "quality"])
        df = df.merge(self.items_info, how="left", on="id")
        df = df.drop_duplicates()
        return df
    
    def close(self):
        """Close the database connection."""
        logger.info("Closing database connection")
        if self.db:
            self.db.close()