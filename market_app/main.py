"""
Main entry point for the Albion Online market analysis application.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_app.cli import MarketCLI

def main():
    """Main entry point for the market application."""
    print("[INFO] Starting Albion Online Market Analysis Application")
    
    # Create and run the CLI
    cli = MarketCLI()
    
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n[INFO] Application terminated by user")
    finally:
        cli.close()
        print("[INFO] Application closed")

if __name__ == "__main__":
    main()