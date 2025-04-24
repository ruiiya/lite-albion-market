"""
Main entry point for the Albion Online market analysis application.
"""
import sys
import os
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

from market_app.cli import MarketCLI

def main():
    """Main entry point for the market application."""
    logger.info("Starting Albion Online Market Analysis Application")
    
    # Create and run the CLI
    cli = MarketCLI()
    
    try:
        cli.run()
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    finally:
        cli.close()
        logger.info("Application closed")

if __name__ == "__main__":
    main()