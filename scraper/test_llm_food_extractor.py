#!/usr/bin/env python3
"""
Test LLM Food Extractor

Tests the new LLM-based food extractor with sample offers.
"""
import json
import sys
import os
from datetime import datetime

# Add the src directory to the path so we can import the llm_food_extractor
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_food_extractor import LLMFoodExtractor

def test_llm_food_extractor():
    """Test the LLM food extractor with sample offers"""
    
    # Initialize the LLM food extractor
    extractor = LLMFoodExtractor()
    
    # Sample offers for testing
    test_offers = [
        {
            "offer_name": "Fjölskyldutilboð",
            "description": "2 Búlluborgarar, 2 barnaborgarar, stór franskar, 2 l gos og 2 kokteilsósur",
            "price_kr": 6000,
            "pickup_delivery": None,
            "suits_people": 4,
            "available_weekdays": None,
            "available_hours": None,
            "restaurant_name": "Búllan"
        },
        {
            "offer_name": "Duo Bucket fyrir 2",
            "description": "Tveir Original kjúklingabitar, tvær Zinger kjúklingalundir, fjórir Hot Wings, tveir skammtar af heitri brúnni sósu, tveir skammtar af frönskum, fjórar Hot Sauce og BBQ Dip-sósa.",
            "price_kr": 454,
            "pickup_delivery": None,
            "suits_people": 2,
            "available_weekdays": None,
            "available_hours": None,
            "restaurant_name": "KFC Iceland"
        },
        {
            "offer_name": "BÁTUR MÁNAÐARINS: GRÆNMETISBÁTUR OG GOS",
            "description": "Grænmetisbátur með gosi",
            "price_kr": 1299,
            "pickup_delivery": None,
            "suits_people": 1,
            "available_weekdays": None,
            "available_hours": None,
            "restaurant_name": "Subway Iceland"
        },
        {
            "offer_name": "HÁDEGISTILBOÐ",
            "description": "Alla daga til kl. 14:00",
            "price_kr": 2495,
            "pickup_delivery": None,
            "suits_people": None,
            "available_weekdays": None,
            "available_hours": None,
            "restaurant_name": "Hlöllabátar"
        }
    ]
    
    print("Testing LLM Food Extractor")
    print("=" * 50)
    
    # Process offers
    enhanced_offers = extractor.extract_food_info_batch(test_offers)
    
    # Display results
    for i, offer in enumerate(enhanced_offers):
        print(f"\nOffer #{i+1}: {offer['offer_name']}")
        print("-" * 40)
        print(f"Description: {offer['description']}")
        print(f"Restaurant: {offer['restaurant_name']}")
        print(f"Price: {offer['price_kr']} kr")
        print()
        
        print("EXTRACTED FOOD INFO:")
        print(f"  Meal Type: {offer.get('meal_type', 'unknown')}")
        print(f"  Is Combo: {offer.get('is_combo', False)}")
        print(f"  Complexity Score: {offer.get('complexity_score', 0)}")
        print(f"  Total Items: {offer.get('total_food_items', 0)}")
        print(f"  Visual Summary: {offer.get('visual_summary', 'N/A')}")
        print()
        
        if offer.get('main_items'):
            print("  Main Items:")
            for item in offer['main_items']:
                print(f"    - {item['quantity']}x {item['name']} ({item['type']})")
        
        if offer.get('side_items'):
            print("  Side Items:")
            for item in offer['side_items']:
                print(f"    - {item['quantity']}x {item['name']} ({item['type']})")
        
        if offer.get('drink_items'):
            print("  Drink Items:")
            for item in offer['drink_items']:
                print(f"    - {item['quantity']}x {item['name']} ({item['type']})")
        
        if offer.get('dessert_items'):
            print("  Dessert Items:")
            for item in offer['dessert_items']:
                print(f"    - {item['quantity']}x {item['name']} ({item['type']})")
        
        if not any([offer.get('main_items'), offer.get('side_items'), 
                   offer.get('drink_items'), offer.get('dessert_items')]):
            print("  No food items extracted")
        
        print()
    
    # Save results to file
    output_filename = f"llm_food_extractor_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(enhanced_offers, f, ensure_ascii=False, indent=2)
    
    print(f"Results saved to: {output_filename}")
    print("Test completed!")

if __name__ == "__main__":
    test_llm_food_extractor() 