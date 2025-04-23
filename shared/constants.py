"""
Shared constants for both collector and market_app components.
"""
from dotenv import load_dotenv
import os

load_dotenv()

# City/location mappings
LOCATIONS = {
    "0007": "Thetford",
    "1002": "Lymhurst",
    "2004": "Bridgewatch",
    "3008": "Martlock",
    "4002": "FortSterling",
    "3005": "Caerleon",
    "3003": "BlackMarket",
    "0301": "Thetford",
    "1301": "Lymhurst",
    "2301": "Bridgewatch",
    "3301": "Martlock",
    "4301": "FortSterling",
    "5003": "Brecilien"
}

# Short names for locations
SHORTNAME = {
    "bw": "Bridgewatch",
    "tf": "Thetford",
    "ml": "Martlock",
    "lh": "Lymhurst",
    "fs": "FortSterling",
    "cl": "Caerleon",
    "bm": "BlackMarket",
    "br": "Brecilien",
    "avg": "Average",
}

# Database constants
DATABASE_PATH = "Market.db"
DATABASE_AVG_PATH = "Average.db"
EXPORT_DIR = "Databases"

# Default settings
DEFAULT_TIER = os.getenv("SET_FILTER_TIER", "")
DEFAULT_DIFF_SHOW = float(os.getenv("LEAST_DIFF_SHOW", "1.3"))
DEFAULT_QUALITIES = [int(i) for i in os.getenv("SET_FILTER_QUALITY", "1,2,3").split(",")]

# Market fee constants
MARKET_TAX = 0.04  # 4% market tax
SETUP_FEE = 0.025  # 2.5% setup fee
TOTAL_FEE = MARKET_TAX + SETUP_FEE  # 6.5% total fee