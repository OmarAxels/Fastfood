#!/usr/bin/env python3
"""
Test script for the website crawler
Tests the crawler on a single restaurant before running on all.
"""

from website_crawler import WebsiteCrawler
import json


def test_single_restaurant():
    """Test the crawler on a single restaurant."""
    # Test restaurant (you can modify this)
    test_restaurant = {
        "name": "Metro",
        "website": "https://www.metro.is"
    }
    
    print("Testing crawler on a single restaurant:")
    print(f"Restaurant: {test_restaurant['name']}")
    print(f"Website: {test_restaurant['website']}")
    
    crawler = WebsiteCrawler()
    
    # Test the crawler on this restaurant
    result = crawler.crawl_restaurant(test_restaurant)
    
    print("\nResult:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result


def test_existing_restaurants():
    """Test the crawler on restaurants that already have menu/offers pages."""
    # Load existing data
    crawler = WebsiteCrawler()
    restaurants = crawler.load_restaurants()
    
    # Find restaurants with existing menu/offers pages
    test_restaurants = []
    for restaurant in restaurants:
        if 'offers_page' in restaurant:
            test_restaurants.append(restaurant)
            if len(test_restaurants) >= 2:  # Test on 2 existing ones
                break
    
    if not test_restaurants:
        print("No restaurants with existing offers pages found for testing")
        return
    
    print(f"Testing on {len(test_restaurants)} restaurants with existing offers pages:")
    
    for restaurant in test_restaurants:
        print(f"\nTesting: {restaurant['name']}")
        result = crawler.crawl_restaurant(restaurant)
        print(f"  Website name extracted: {crawler.extract_website_name(restaurant['website'])}")


def main():
    """Run the tests."""
    print("=== Website Crawler Test Suite ===\n")
    
    # Test 1: Single restaurant without menu/offers pages
    print("Test 1: Single restaurant discovery")
    print("-" * 40)
    test_single_restaurant()
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Restaurants with existing offers pages (HTML download test)
    print("Test 2: Existing restaurants (HTML download)")
    print("-" * 40)
    test_existing_restaurants()
    
    print("\n" + "="*50)
    print("Tests completed!")
    print("\nTo run the full crawler on all restaurants, run:")
    print("python website_crawler.py")


if __name__ == "__main__":
    main() 