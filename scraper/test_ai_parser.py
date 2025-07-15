#!/usr/bin/env python3
"""
Test script for the new AI parser
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from parsers.ai_parser import AIParser

def test_ai_parser():
    """Test the AI parser with KFC"""
    print("Testing AI Parser...")
    
    parser = AIParser()
    
    # Test with KFC URL
    url = "https://www.kfc.is/menu"
    
    print(f"Scraping offers from: {url}")
    offers = parser.scrape_offers(url)
    
    print(f"\nFound {len(offers)} offers:")
    for i, offer in enumerate(offers, 1):
        print(f"\n{i}. {offer.get('offer_name', 'No name')}")
        print(f"   Description: {offer.get('description', 'No description')}")
        print(f"   Price: {offer.get('price_kr', 'No price')} kr")
    
    return offers

if __name__ == "__main__":
    test_ai_parser() 