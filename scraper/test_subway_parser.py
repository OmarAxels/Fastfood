#!/usr/bin/env python3
"""
Test script for the Subway parser
Tests the parser using the downloaded subway.html file and live website.
"""

import sys
import os
import json
from bs4 import BeautifulSoup

# Add the src directory to the path so we can import the parsers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parsers.subway_parser import SubwayParser


def test_subway_parser_with_html_file():
    """Test the Subway parser using the downloaded HTML file"""
    print("Testing Subway parser with local HTML file...")
    
    # Read the downloaded subway.html file
    html_file_path = os.path.join(os.path.dirname(__file__), 'offers_pages', 'subway.html')
    
    if not os.path.exists(html_file_path):
        print(f"Error: {html_file_path} not found")
        return
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Create parser instance
    parser = SubwayParser()
    
    # Test the script extraction methods directly
    print("\n=== Testing script extraction ===")
    offers_from_scripts = parser._extract_offers_from_scripts(soup)
    print(f"Found {len(offers_from_scripts)} offers from scripts")
    
    for i, offer in enumerate(offers_from_scripts[:5]):  # Show first 5
        print(f"  {i+1}. {offer}")
    
    # Test the content-based extraction
    print("\n=== Testing content-based extraction ===")
    offers_from_content = parser._find_offers_by_content(soup)
    print(f"Found {len(offers_from_content)} potential offers from content")
    
    # Test full extraction process
    print("\n=== Testing full extraction process ===")
    for offer_element in offers_from_scripts[:3]:  # Test first 3
        extracted_offer = parser._extract_offer_data(offer_element)
        print(f"Extracted offer: {json.dumps(extracted_offer, indent=2, ensure_ascii=False)}")
        print("-" * 50)


def test_subway_parser_live():
    """Test the Subway parser with the live website"""
    print("\n" + "="*60)
    print("Testing Subway parser with live website...")
    
    parser = SubwayParser()
    
    try:
        # Test with the main Subway website (offers page)
        offers = parser.scrape_offers("https://www.subway.is")
        
        print(f"\nFound {len(offers)} offers from live website:")
        
        for i, offer in enumerate(offers, 1):
            print(f"\n{i}. {offer['offer_name']}")
            if offer['description']:
                print(f"   Description: {offer['description']}")
            if offer['price_kr']:
                print(f"   Price: {offer['price_kr']} kr")
            if offer['available_weekdays']:
                print(f"   Available: {offer['available_weekdays']}")
            if offer['suits_people']:
                print(f"   Suits: {offer['suits_people']} people")
            if offer['pickup_delivery']:
                print(f"   Service: {offer['pickup_delivery']}")
    
    except Exception as e:
        print(f"Error testing live website: {e}")


def test_icelandic_day_mapping():
    """Test the Icelandic day name mapping"""
    print("\n=== Testing Icelandic day mapping ===")
    
    parser = SubwayParser()
    
    test_days = [
        'Mánudagur', 'Þriðjudagur', 'Miðvikudagur', 'Fimmtudagur',
        'Föstudagur', 'Laugardagur', 'Sunnudagur'
    ]
    
    for day in test_days:
        mapped = parser._map_icelandic_day_to_weekday(day)
        print(f"  {day} -> {mapped}")


def test_regex_patterns():
    """Test the regex patterns with sample data"""
    print("\n=== Testing regex patterns ===")
    
    parser = SubwayParser()
    
    # Sample script content similar to what's in subway.html
    sample_script = '''
    "day_name":"Mánudagur","product_name":"Kalkúnn og Skinka","cta_link":"/deals/123/"
    "day_name":"Þriðjudagur","product_name":"Ítalskur BMT","cta_link":"/deals/456/"
    "text":"50% afsláttur af öllum bátum"
    "text":"Einungis á vef og í appi"
    "button_text":"panta","description":[{"type":"paragraph","text":"Matur eftir þínu höfði"}]
    '''
    
    daily_offers = parser._parse_daily_offers_from_script(sample_script)
    print(f"Found {len(daily_offers)} daily offers from sample:")
    for offer in daily_offers:
        print(f"  - {offer}")
    
    promo_offers = parser._parse_promotional_offers_from_script(sample_script)
    print(f"Found {len(promo_offers)} promotional offers from sample:")
    for offer in promo_offers:
        print(f"  - {offer}")


def main():
    """Run all tests"""
    print("=== Subway Parser Test Suite ===")
    
    # Test 1: HTML file parsing
    test_subway_parser_with_html_file()
    
    # Test 2: Regex patterns
    test_regex_patterns()
    
    # Test 3: Day mapping
    test_icelandic_day_mapping()
    
    # Test 4: Live website (optional)
    try_live = input("\nTest with live website? (y/n): ").lower().strip()
    if try_live in ['y', 'yes']:
        test_subway_parser_live()
    
    print("\n" + "="*60)
    print("Subway parser tests completed!")


if __name__ == "__main__":
    main() 