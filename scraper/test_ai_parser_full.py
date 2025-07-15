#!/usr/bin/env python3
"""
Full test of the AI parser integration without database
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from parsers.ai_parser import AIParser
from json_reader import FastfoodInfoReader

def test_ai_parser_integration():
    """Test the AI parser with the full scraping workflow"""
    print("Testing AI Parser Integration...")
    
    # Load restaurant data
    json_reader = FastfoodInfoReader("fastfood-info.json")
    restaurants = json_reader.load_restaurants()
    
    # Find KFC restaurant
    kfc_restaurant = None
    for restaurant in restaurants:
        if restaurant['name'] == 'KFC Iceland':
            kfc_restaurant = restaurant
            break
    
    if not kfc_restaurant:
        print("KFC Iceland not found in restaurant data")
        return
    
    print(f"Testing with restaurant: {kfc_restaurant['name']}")
    print(f"URL: {kfc_restaurant['offers_page']}")
    
    # Test AI parser
    parser = AIParser()
    offers = parser.scrape_offers(kfc_restaurant['offers_page'])
    
    print(f"\nFound {len(offers)} offers:")
    for i, offer in enumerate(offers, 1):
        print(f"\n{i}. {offer.get('offer_name', 'No name')}")
        print(f"   Description: {offer.get('description', 'No description')}")
        print(f"   Price: {offer.get('price_kr', 'No price')} kr")
    
    # Test the enhance_offers_with_food_info method
    print("\n" + "="*50)
    print("Testing offer enhancement...")
    
    enhanced_offers = parser.enhance_offers_with_food_info(offers)
    
    print(f"Enhanced {len(enhanced_offers)} offers:")
    for i, offer in enumerate(enhanced_offers, 1):
        print(f"\n{i}. {offer.get('offer_name', 'No name')}")
        print(f"   Description: {offer.get('description', 'No description')}")
        print(f"   Price: {offer.get('price_kr', 'No price')} kr")
        print(f"   Food items: {offer.get('food_items', [])}")
    
    return offers

if __name__ == "__main__":
    test_ai_parser_integration() 