"""
Shared database operations for both collector and market_app components.
"""
import sqlite3
import pandas as pd
import os
from datetime import datetime, timezone
from .constants import DATABASE_PATH, DATABASE_AVG_PATH, EXPORT_DIR
from .filter import regex_filter

class MarketDatabase:
    """Handles database operations for the market data system."""
    
    def __init__(self, db_path=DATABASE_PATH):
        """Initialize the database connection."""
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to the database."""
        if not self.conn:
            if not os.path.exists(os.path.dirname(self.db_path)) and os.path.dirname(self.db_path):
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.conn
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def ensure_table_exists(self, location):
        """
        Make sure the table for a given location exists.
        
        Args:
            location: The location name (e.g., "BlackMarket")
        """
        conn = self.connect()
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {location} (
                id TEXT,
                quality INT,
                enchant INT,
                sell_min INT,
                buy_max INTEGER,
                sell_min_datetime DATETIME,
                buy_max_datetime DATETIME
            )
        """)
        conn.commit()
    
    def update_sell_order(self, location, item_id, quality, enchant, price):
        """
        Update a sell order in the database.
        
        Args:
            location: The location name (e.g., "BlackMarket")
            item_id: The item identifier
            quality: The quality level
            enchant: The enchantment level
            price: The price in silver
        """
        self.ensure_table_exists(location)
        conn = self.connect()
        cur = conn.cursor()
        
        # Check if record exists
        entry = cur.execute(
            f"SELECT * FROM {location} WHERE id = ? AND quality = ?", 
            (item_id, quality)
        ).fetchone()
        
        if entry is None:
            # Insert new record
            cur.execute(
                f"INSERT INTO {location}(id, quality, sell_min, sell_min_datetime, enchant) VALUES(?, ?, ?, ?, ?)", 
                (item_id, quality, price, datetime.now(timezone.utc), enchant)
            )
            print(f"[INFO] Added new sell order for item {item_id} at location {location} with price {price}.")
        else:
            # Update existing record if price is lower or data is outdated
            if entry[3] is None or price < entry[3] or \
               entry[5] is None or (datetime.now(timezone.utc) - datetime.fromisoformat(entry[5])).total_seconds() / 60 > 30:
                cur.execute(
                    f"UPDATE {location} SET sell_min = ?, sell_min_datetime = ? WHERE id = ? AND quality = ?", 
                    (price, datetime.now(timezone.utc), item_id, quality)
                )
                
                print(f"[INFO] Updated sell order for item {item_id} at location {location} with price {price}.")
        
        conn.commit()
    
    def update_buy_order(self, location, item_id, quality, enchant, price):
        """
        Update a buy order in the database.
        
        Args:
            location: The location name (e.g., "BlackMarket")
            item_id: The item identifier
            quality: The quality level
            enchant: The enchantment level
            price: The price in silver
        """
        self.ensure_table_exists(location)
        conn = self.connect()
        cur = conn.cursor()
        
        # Check if record exists
        entry = cur.execute(
            f"SELECT * FROM {location} WHERE id = ? AND quality = ?", 
            (item_id, quality)
        ).fetchone()
        
        if entry is None:
            # Insert new record
            cur.execute(
                f"INSERT INTO {location}(id, quality, buy_max, buy_max_datetime, enchant) VALUES(?, ?, ?, ?, ?)", 
                (item_id, quality, price, datetime.now(timezone.utc), enchant)
            )
            print(f"[INFO] Added new buy order for item {item_id} at location {location} with price {price}.")
        else:
            # Update existing record if price is higher or data is outdated
            if entry[4] is None or price > entry[4] or \
               entry[6] is None or (datetime.now(timezone.utc) - datetime.fromisoformat(entry[6])).total_seconds() / 60 > 30:
                cur.execute(
                    f"UPDATE {location} SET buy_max = ?, buy_max_datetime = ? WHERE id = ? AND quality = ?", 
                    (price, datetime.now(timezone.utc), item_id, quality)
                )
                
                print(f"[INFO] Updated buy order for item {item_id} at location {location} with price {price}.")
        
        conn.commit()
    
    def get_location_data(self, location, filter_obj=None):
        """
        Get data for a specific location with optional filtering.
        
        Args:
            location: The location name (e.g., "BlackMarket")
            filter_obj: Optional Filter object to filter the data
            
        Returns:
            DataFrame containing the filtered data
        """
        conn = self.connect()
        
        # Check if the table exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{location}'")
        if not cursor.fetchone():
            print(f"No table found for {location}")
            return pd.DataFrame()
        
        # Get the data
        df = pd.read_sql_query(f"SELECT * FROM {location}", conn)
        if df.empty:
            print(f"No data found for {location}")
            return pd.DataFrame()
        
        # Apply filtering if provided
        if filter_obj:
            df = df.sort_values(by=["id", "quality"])
            df = df[df.quality.isin(filter_obj.qualities)]
            df = df[df["id"].apply(regex_filter, filters=filter_obj.tiers)]
        
        return df
    
    def export_to_csv(self, location, filter_obj=None):
        """
        Export data for a location to a CSV file.
        
        Args:
            location: The location name (e.g., "BlackMarket")
            filter_obj: Optional Filter object to filter the data
            
        Returns:
            Path to the created CSV file
        """
        df = self.get_location_data(location, filter_obj)
        if df.empty:
            return None
        
        os.makedirs(EXPORT_DIR, exist_ok=True)
        csv_path = f'{EXPORT_DIR}/{location}.csv'
        df.to_csv(csv_path, index=False)
        return csv_path
    
    def delete_location_data(self, location):
        """
        Delete all data for a specific location.
        
        Args:
            location: The location name (e.g., "BlackMarket")
            
        Returns:
            True if successful, False otherwise
        """
        conn = self.connect()
        
        # Check if the table exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{location}'")
        if not cursor.fetchone():
            print(f"No table found for {location}")
            return False
        
        # Delete the data
        cursor.execute(f"DELETE FROM {location}")
        conn.commit()
        return True