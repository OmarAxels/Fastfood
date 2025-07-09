#!/usr/bin/env python3
"""
Fastfood Scraper - Scrapes special offers from Icelandic fastfood websites
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from scraper import FastfoodScraper
from database import DatabaseManager


def main():
    """Main entry point for the fastfood scraper"""
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.create_tables()
        
        # Initialize and run scraper
        scraper = FastfoodScraper(db_manager)
        scraper.run()
        
        logging.info("Scraping completed successfully")
        
    except Exception as e:
        logging.error(f"Scraping failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 