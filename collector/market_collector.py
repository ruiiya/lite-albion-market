"""
Core functionality for collecting market data from Albion Online.
"""
import json
import pandas as pd
from datetime import datetime, timezone
import sys
import os
import logging
from typing import List, Any, Tuple, Union, Dict

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import MarketDatabase
from shared.constants import LOCATIONS

class MarketCollector:
    """
    Handles the collection of market data from Albion Online game.
    Uses photon networking interception to gather market orders.
    """
    
    def __init__(self):
        """Initialize the market data collector."""
        logger.info("Initializing MarketCollector")
        self.db = MarketDatabase()
        self.player_location = None
        self.location_name = None
        self.items_info = pd.read_csv("shared/items.csv")
        logger.debug(f"Loaded {len(self.items_info)} items from items.csv")
    
    def set_player_location(self, location_code):
        """
        Set the current player location.
        
        Args:
            location_code: The location code from the game
        """
        self.player_location = location_code
        self.location_name = None if location_code not in LOCATIONS else LOCATIONS[location_code]
        
        if self.location_name:
            # Create the table for this location if it doesn't exist
            self.db.ensure_table_exists(self.location_name)
            logger.info(f"Update player location: {self.player_location} ({self.location_name})")
        else:
            logger.info(f"Update player location: {self.player_location} (Unknown location)")
    
    def parse_order(self, data: Union[List[str], Dict, Any]) -> List[Tuple[str, int, int, int]]:
        """
        Parse order data from the network packets.
        
        Args:
            data: Order data in various formats (list, dict, or single item)
            
        Returns:
            List of tuples containing (item_id, price, quality, enchant)
        """
        result = []
        
        # Debug logging to understand data structure
        logger.debug(f"Data type: {type(data)}")
        if isinstance(data, int):
            logger.debug("Received integer data, no orders to parse")
            return []
        try:
            if isinstance(data, list):
                for item in data:
                    item = json.loads(item) if isinstance(item, str) else item
                    if isinstance(item, dict):
                        item_id = item.get("ItemTypeId")
                        price = item.get("UnitPriceSilver") / 10000
                        quality = item.get("QualityLevel", 0)
                        enchant = item.get("EnchantmentLevel", 0)
                        result.append((item_id, price, quality, enchant))
                    else:
                        logger.warning(f"Unexpected item format: {item}")
                        print(f"[WARN] Unexpected item format: {item}")
            else:
                logger.warning(f"Expected list but got {type(data)}")
        except Exception as e:
            logger.error(f"Parsing order data: {str(e)}", exc_info=True)
            
        return result
    
    def process_sell_orders(self, parameters):
        """
        Process sell orders received from the game.
        
        Args:
            parameters: Raw parameters from the network packet
        """
        if self.db is None or self.location_name is None:
            logger.warning("SELL_ORDER: Unknown player location")
            return
        
        try:
            # Extract order data from parameters
            orders = self.parse_order(parameters[0])
            
            if not orders:
                logger.debug("SELL_ORDER: No valid orders to process")
                return
                
            for item_id, price, quality, enchant in orders:
                self.db.update_sell_order(self.location_name, item_id, quality, enchant, price)
            
            logger.info(f"[{self.player_location}] SELL_ORDER: Processed {len(orders)} orders")
        except Exception as e:
            logger.error(f"Processing sell orders: {str(e)}", exc_info=True)
    
    def process_buy_orders(self, parameters):
        """
        Process buy orders received from the game.
        
        Args:
            parameters: Raw parameters from the network packet
        """
        if self.db is None or self.location_name is None:
            logger.warning("BUY_ORDER: Unknown player location")
            return
        
        try:
            # Extract order data from parameters
            orders = self.parse_order(parameters[0])
            
            if not orders:
                logger.debug("BUY_ORDER: No valid orders to process")
                return
                
            for item_id, price, quality, enchant in orders:
                self.db.update_buy_order(self.location_name, item_id, quality, enchant, price)
            
            logger.info(f"[{self.player_location}] BUY_ORDER: Processed {len(orders)} orders")
        except Exception as e:
            logger.error(f"Processing buy orders: {str(e)}", exc_info=True)
    
    def close(self):
        """Close the database connection."""
        logger.info("Closing database connection")
        if self.db:
            self.db.close()