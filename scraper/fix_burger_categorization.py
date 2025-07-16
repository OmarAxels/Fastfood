#!/usr/bin/env python3
"""
Fix burger categorization in enhanced offers data
"""
import json
import re

def fix_burger_categorization():
    """Fix burger categorization in the enhanced offers data"""
    
    # Load the enhanced offers data
    with open('enhanced_offers_with_food_info.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Burger terms to look for
    burger_terms = ['búlluborgari', 'búlluborgarar', 'barnaborgari', 'barnaborgarar', 'hamborgari', 'borgari', 'burger']
    
    fixed_count = 0
    
    for offer in data['offers']:
        description = offer.get('description', '').lower()
        offer_name = offer.get('offer_name', '').lower()
        full_text = f"{offer_name} {description}"
        
        # Check if this offer contains burger terms
        found_burgers = []
        for term in burger_terms:
            if term in full_text:
                # Extract quantity for this burger type
                quantity = extract_burger_quantity(full_text, term)
                if quantity > 0:
                    found_burgers.append({
                        'type': 'burger',
                        'name': term,
                        'category': 'main',
                        'icon': '🍔',
                        'quantity': quantity,
                        'size': None,
                        'modifiers': [],
                        'phrase': f"{quantity} {term}"
                    })
        
        # If we found burgers, add them to main_items
        if found_burgers:
            # Initialize main_items if it doesn't exist
            if 'main_items' not in offer:
                offer['main_items'] = []
            
            # Add the found burgers to main_items
            offer['main_items'].extend(found_burgers)
            
            # Also add to food_items if it exists
            if 'food_items' in offer:
                offer['food_items'].extend(found_burgers)
            
            fixed_count += 1
            print(f"Fixed offer: {offer.get('offer_name', 'Unknown')}")
    
    # Save the fixed data
    with open('enhanced_offers_with_food_info_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Fixed {fixed_count} offers with burger categorization")
    print("Saved to enhanced_offers_with_food_info_fixed.json")

def extract_burger_quantity(text, burger_term):
    """Extract quantity for a specific burger term"""
    # Look for patterns like "2 Búlluborgarar" or "2 barnaborgarar"
    pattern = rf'(\d+)\s*{re.escape(burger_term)}'
    match = re.search(pattern, text)
    if match:
        return int(match.group(1))
    
    # Look for Icelandic number words
    icelandic_numbers = {
        'einn': 1, 'ein': 1, 'eitt': 1,
        'tveir': 2, 'tvær': 2, 'tvö': 2,
        'þrír': 3, 'þrjár': 3, 'þrjú': 3,
        'fjórir': 4, 'fjórar': 4, 'fjögur': 4,
        'fimm': 5, 'sex': 6, 'sjö': 7, 'átta': 8, 'níu': 9, 'tíu': 10
    }
    
    for icelandic_num, value in icelandic_numbers.items():
        pattern = rf'{icelandic_num}\s*{re.escape(burger_term)}'
        if re.search(pattern, text):
            return value
    
    # Default to 1 if no quantity found
    return 1

if __name__ == "__main__":
    fix_burger_categorization() 