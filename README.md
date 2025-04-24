# Lite Albion Market 3.0

A modular Albion Online market data collection and analysis tool.

## System Overview

The system is divided into three main components:

1. **Data Collector**: Captures market data from Albion Online
2. **Market Application (CLI)**: Command-line interface for analyzing market data
3. **Market Application (GUI)**: Web-based interface for visualizing and analyzing market data

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

### Market Application (CLI)

To analyze and view market data in the command-line interface:

```bash
run_market_app.bat
# OR
python market_app/main.py
```

### Market Application (GUI)

To use the web-based graphical interface:

```bash
run_gui.bat
# OR
python web/eel_app.py
```

The GUI provides an interactive interface with:
- Market data visualization
- Quick sell opportunity analysis
- Sell order opportunity analysis
- Various filtering options for tier, quality, and profit ratio

## Market Application Commands (CLI)

The command-line interface supports the following commands:

| Command | Description |
|---------|-------------|
| `help` | Show help information |
| `csv [locations]` | Export data to CSV files |
| `clear [locations]` | Clear data for specified locations |
| `set tier [tiers]` | Set tier filter (e.g., '4.0 5.1 6.2') |
| `set quality [quals]` | Set quality filter (e.g., '1 2 3') |
| `set diff [num]` | Set minimum profit ratio (e.g., '1.3') |
| `bulk [locations]` | Compare black market with royal cities |
| `show` | Show current filter settings |
| `show all` | Show data for all locations with current filters |
| `show [locations]` | Show data for specified locations |
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
