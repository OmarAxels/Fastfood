#!/usr/bin/env python3
"""
Script to examine current offers and their structure
"""
import sys
import os
sys.path.append('src')

from parsers.kfc_parser import KFCParser
from parsers.dominos_parser import DominosParser
from parsers.subway_parser import SubwayParser

def examine_restaurant_offers(parser_class, name, url):
    """Examine offers from a specific restaurant"""
    print(f"\n=== {name} OFFERS ===")
    try:
        parser = parser_class()
        offers = parser.scrape_offers(url)
        
        for i, offer in enumerate(offers, 1):
            print(f"\n{i}. {offer.get('offer_name', 'Unknown')}")
            if offer.get('description'):
                print(f"   Description: {offer['description']}")
            if offer.get('price_kr'):
                print(f"   Price: {offer['price_kr']} kr")
            if offer.get('suits_people'):
                print(f"   Serves: {offer['suits_people']} people")
            print(f"   Raw data: {offer}")
                
        print(f"\nTotal offers found: {len(offers)}")
        
    except Exception as e:
        print(f"Error examining {name}: {e}")

def main():
    # Examine offers from each restaurant
    restaurants = [
        (KFCParser, "KFC Iceland", "https://www.kfc.is/menu#category_tilbod"),
        (DominosParser, "Domino's Pizza Iceland", "https://www.dominos.is/panta/tilbod"),
        (SubwayParser, "Subway Iceland", "https://subway.is/menu#tilbod")
    ]
    
    for parser_class, name, url in restaurants:
        examine_restaurant_offers(parser_class, name, url)

if __name__ == "__main__":
    main() 