# Lite Albion Market 3.0

A modular Albion Online market data collection and analysis tool.

## System Overview

The system is divided into two main components:

1. **Data Collector**: Captures market data from Albion Online
2. **Market Application**: Analyzes and displays market data

## Installation

```bash
pip install -r requirements.txt
```

## Running the System

### Data Collector

To start collecting market data:

```bash
run_collector.bat
# OR
python collector/main.py
```

The data collector will capture market data while you play Albion Online. It will:
- Detect your current city/location
- Record buy and sell orders
- Store data in the Market.db database

For best results, visit the marketplace in each city to collect current prices.

### Market Application

To analyze and view market data:

```bash
run_market_app.bat
# OR
python market_app/main.py
```

## Market Application Commands

The market application supports the following commands:

| Command | Description |
|---------|-------------|
| `help` | Show help information |
| `csv [locations]` | Export data to CSV files |
| `clear [locations]` | Clear data for specified locations |
| `set tier [tiers]` | Set tier filter (e.g., '4.0 5.1 6.2') |
| `set quality [quals]` | Set quality filter (e.g., '1 2 3') |
| `set diff [num]` | Set minimum profit ratio (e.g., '1.3') |
| `bulk [locations]` | Compare black market with royal cities |
| `exit` | Exit the application |

## Location Shortcuts

| Shortcut | Location |
|----------|----------|
| bw | Bridgewatch |
| tf | Thetford |
| ml | Martlock |
| lh | Lymhurst |
| fs | FortSterling |
| cl | Caerleon |
| bm | BlackMarket |
| br | Brecilien |

## Example Usage

```
> set tier 6.0 6.1 7.0 7.1
> set quality 1 2 3
> set diff 1.3
> bulk lh ml
```

This will compare Lymhurst and Martlock markets with the Black Market, showing items with at least a 1.3x profit margin in tiers 6.0, 6.1, 7.0, and 7.1 with quality levels 1-3.