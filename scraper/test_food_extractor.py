#!/usr/bin/env python3
"""
Test Food Extractor

Tests the food extractor with all current descriptions from the enhanced offers data
and saves the output to a text file for analysis.
"""
import json
import sys
import os
from datetime import datetime

# Add the src directory to the path so we can import the food_extractor
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from food_extractor import FoodExtractor

def test_food_extractor():
    """Test the food extractor with all current descriptions"""
    
    # Initialize the food extractor
    extractor = FoodExtractor()
    
    # Load the enhanced offers data
    try:
        with open('enhanced_offers_with_food_info_fixed.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: enhanced_offers_with_food_info_fixed.json not found")
        print("Please run the fix_burger_categorization.py script first")
        return
    
    # Prepare output
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("FOOD EXTRACTOR TEST RESULTS")
    output_lines.append("=" * 80)
    output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"Total offers tested: {len(data['offers'])}")
    output_lines.append("")
    
    # Statistics
    stats = {
        'total_offers': len(data['offers']),
        'offers_with_food': 0,
        'offers_with_main_items': 0,
        'offers_with_side_items': 0,
        'offers_with_drink_items': 0,
        'offers_with_dessert_items': 0,
        'meal_types': {},
        'food_types_found': set()
    }
    
    # Test each offer
    for i, offer in enumerate(data['offers'], 1):
        offer_name = offer.get('offer_name', 'Unknown')
        description = offer.get('description', '')
        
        output_lines.append(f"Offer #{i}: {offer_name}")
        output_lines.append("-" * 60)
        output_lines.append(f"Description: {description}")
        output_lines.append("")
        
        # Extract food info using the extractor
        food_info = extractor.extract_food_info(offer_name, description)
        
        # Display extracted food items
        output_lines.append("EXTRACTED FOOD ITEMS:")
        
        if food_info['main_items']:
            output_lines.append("  Main Items:")
            for item in food_info['main_items']:
                output_lines.append(f"    - {item['quantity']}x {item['name']} ({item['type']})")
                stats['food_types_found'].add(item['type'])
            stats['offers_with_main_items'] += 1
        
        if food_info['side_items']:
            output_lines.append("  Side Items:")
            for item in food_info['side_items']:
                output_lines.append(f"    - {item['quantity']}x {item['name']} ({item['type']})")
                stats['food_types_found'].add(item['type'])
            stats['offers_with_side_items'] += 1
        
        if food_info['drink_items']:
            output_lines.append("  Drink Items:")
            for item in food_info['drink_items']:
                output_lines.append(f"    - {item['quantity']}x {item['name']} ({item['type']})")
                stats['food_types_found'].add(item['type'])
            stats['offers_with_drink_items'] += 1
        
        if food_info['dessert_items']:
            output_lines.append("  Dessert Items:")
            for item in food_info['dessert_items']:
                output_lines.append(f"    - {item['quantity']}x {item['name']} ({item['type']})")
                stats['food_types_found'].add(item['type'])
            stats['offers_with_dessert_items'] += 1
        
        if not any([food_info['main_items'], food_info['side_items'], 
                   food_info['drink_items'], food_info['dessert_items']]):
            output_lines.append("  No food items extracted")
        
        # Display meal type and complexity
        output_lines.append(f"  Meal Type: {food_info['meal_type']}")
        output_lines.append(f"  Complexity Score: {food_info['complexity_score']}")
        output_lines.append(f"  Total Items: {food_info['total_items']}")
        output_lines.append(f"  Is Combo: {food_info['is_combo']}")
        
        # Track meal type statistics
        meal_type = food_info['meal_type']
        stats['meal_types'][meal_type] = stats['meal_types'].get(meal_type, 0) + 1
        
        if food_info['food_items']:
            stats['offers_with_food'] += 1
        
        output_lines.append("")
        output_lines.append("ORIGINAL DATA (for comparison):")
        
        # Show original data for comparison
        if offer.get('main_items'):
            output_lines.append("  Original Main Items:")
            for item in offer['main_items']:
                output_lines.append(f"    - {item['quantity']}x {item['name']} ({item['type']})")
        
        if offer.get('side_items'):
            output_lines.append("  Original Side Items:")
            for item in offer['side_items']:
                output_lines.append(f"    - {item['quantity']}x {item['name']} ({item['type']})")
        
        if offer.get('drink_items'):
            output_lines.append("  Original Drink Items:")
            for item in offer['drink_items']:
                output_lines.append(f"    - {item['quantity']}x {item['name']} ({item['type']})")
        
        if offer.get('dessert_items'):
            output_lines.append("  Original Dessert Items:")
            for item in offer['dessert_items']:
                output_lines.append(f"    - {item['quantity']}x {item['name']} ({item['type']})")
        
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("")
    
    # Add summary statistics
    output_lines.append("SUMMARY STATISTICS")
    output_lines.append("=" * 80)
    output_lines.append(f"Total offers: {stats['total_offers']}")
    output_lines.append(f"Offers with food items: {stats['offers_with_food']}")
    output_lines.append(f"Offers with main items: {stats['offers_with_main_items']}")
    output_lines.append(f"Offers with side items: {stats['offers_with_side_items']}")
    output_lines.append(f"Offers with drink items: {stats['offers_with_drink_items']}")
    output_lines.append(f"Offers with dessert items: {stats['offers_with_dessert_items']}")
    output_lines.append("")
    
    output_lines.append("MEAL TYPE DISTRIBUTION:")
    for meal_type, count in sorted(stats['meal_types'].items()):
        percentage = (count / stats['total_offers']) * 100
        output_lines.append(f"  {meal_type}: {count} ({percentage:.1f}%)")
    
    output_lines.append("")
    output_lines.append("FOOD TYPES FOUND:")
    for food_type in sorted(stats['food_types_found']):
        output_lines.append(f"  - {food_type}")
    
    # Save to file
    output_filename = f"food_extractor_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Test completed! Results saved to: {output_filename}")
    print(f"Total offers tested: {stats['total_offers']}")
    print(f"Offers with food items: {stats['offers_with_food']}")
    print(f"Food types found: {len(stats['food_types_found'])}")

if __name__ == "__main__":
    test_food_extractor() 