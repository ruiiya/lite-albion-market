"""
Eel-based GUI for the Albion Online market analysis application.
"""
import sys
import os
import logging
import pandas as pd
import eel

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_app.market_analyzer import MarketAnalyzer
from shared.filter import Filter
from shared.constants import SHORTNAME, LOCATIONS

# Initialize Eel
eel.init('web')  # Specify the web directory containing HTML/JS/CSS

# Global instance of our application
app_instance = None

# Exposed functions for Eel - these are standalone functions that use the global app_instance
@eel.expose
def get_locations():
    """Return all available locations for the frontend."""
    locations = {short: full for short, full in SHORTNAME.items()}
    return locations

@eel.expose
def get_market_data(location):
    """Get market data for a specific location with filtering."""
    global app_instance
    logger.info(f"Getting market data for {location}")
    location = SHORTNAME.get(location, location)
    df = app_instance.analyzer.get_location_data(location, app_instance.filter)
    
    if df.empty:
        return {"success": False, "message": f"No data found for {location}"}
        
    # Convert DataFrame to JSON-serializable format
    result = df.to_dict(orient='records')
    return {"success": True, "data": result}

@eel.expose
def compare_markets(royal_city):
    """Compare a royal city market with the black market."""
    global app_instance
    logger.info(f"Comparing {royal_city} with BlackMarket")
    royal_city = SHORTNAME.get(royal_city, royal_city)
    
    comparison = app_instance.analyzer.compare_markets(royal_city, app_instance.filter)
    
    if comparison.empty:
        return {"success": False, "message": f"No comparison data available for {royal_city}"}
    
    # Process quick sell opportunities
    df_qs = comparison[["name", "enchant", "sell_min_rl", "buy_max_bm", 
                      "diff_quick_sell", "quick_sell_desired"]]
    df_qs = df_qs[df_qs["diff_quick_sell"] > app_instance.filter.diff_show]
    
    # Process sell order opportunities
    df_so = comparison[["name", "enchant", "sell_min_rl", "sell_min_bm", 
                      "diff_sell_order", "sell_order_desired"]]
    df_so = df_so[df_so["diff_sell_order"] > app_instance.filter.diff_show]
    
    # Convert DataFrames to JSON-serializable format
    qs_data = df_qs.to_dict(orient='records')
    so_data = df_so.to_dict(orient='records')
    
    return {
        "success": True, 
        "quick_sell": qs_data, 
        "sell_order": so_data
    }

@eel.expose
def export_to_csv(location):
    """Export market data to CSV file."""
    global app_instance
    logger.info(f"Exporting {location} data to CSV")
    location = SHORTNAME.get(location, location)
    
    result = app_instance.analyzer.export_location_to_csv(location, app_instance.filter)
    
    if result:
        return {"success": True, "message": f"Data exported to {result}"}
    else:
        return {"success": False, "message": f"Failed to export data for {location}"}

@eel.expose
def clear_location_data(location):
    """Clear market data for a location."""
    global app_instance
    logger.info(f"Clearing data for {location}")
    location = SHORTNAME.get(location, location)
    
    result = app_instance.analyzer.clear_location_data(location)
    
    if result:
        return {"success": True, "message": f"Data cleared for {location}"}
    else:
        return {"success": False, "message": f"Failed to clear data for {location}"}

@eel.expose
def set_tier_filter(tiers):
    """Set tier filter."""
    global app_instance
    logger.info(f"Setting tier filter: {tiers}")
    app_instance.filter.set_tier(tiers)
    return {"success": True, "message": f"Tier filter set to {tiers}"}

@eel.expose
def set_quality_filter(qualities):
    """Set quality filter."""
    global app_instance
    logger.info(f"Setting quality filter: {qualities}")
    
    # Convert the space-separated quality string to a list of integers
    if qualities and qualities.strip():
        qualities_list = [int(q) for q in qualities.split() if q.isdigit()]
    else:
        qualities_list = []
    
    app_instance.filter.set_quality(qualities_list)
    return {"success": True, "message": f"Quality filter set to {qualities_list}"}

@eel.expose
def set_diff_filter(diff):
    """Set minimum price difference filter."""
    global app_instance
    logger.info(f"Setting difference filter: {diff}")
    app_instance.filter.set_diff(float(diff))
    return {"success": True, "message": f"Difference filter set to {diff}"}

@eel.expose
def get_current_filters():
    """Get current filter settings."""
    global app_instance
    return {
        "tier": app_instance.filter.get_tier(),
        "quality": app_instance.filter.get_quality(),
        "diff": app_instance.filter.get_diff()
    }

class EelMarketApp:
    """
    Eel-based GUI for interacting with the Albion Online market data.
    """
    
    def __init__(self):
        """Initialize the Eel-based market application."""
        logger.info("Initializing Eel Market Application")
        self.analyzer = MarketAnalyzer()
        self.filter = Filter()
        logger.info("Using Market.db database with separate tables")
    
    def close(self):
        """Close the analyzer and clean up resources."""
        logger.info("Closing Eel app resources")
        if self.analyzer:
            self.analyzer.close()

def main():
    """Main entry point for the Eel-based market application."""
    logger.info("Starting Albion Online Market Eel Application")
    
    global app_instance
    app_instance = EelMarketApp()
    
    try:
        # Start the Eel app
        eel.start('index.html', size=(1200, 800))
    except Exception as e:
        logger.error(f"Error in Eel application: {e}")
    finally:
        app_instance.close()
        logger.info("Eel application closed")

if __name__ == "__main__":
    main()