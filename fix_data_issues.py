#!/usr/bin/env python3
"""
Fix Data Issues Script

Fixes two main issues:
1. KFC prices that are missing a digit (multiply by 10)
2. Incorrect family meal_type classification (should only be family if "fjölskyldu" appears in text)
"""

import json
import os
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_kfc_pricing(offer: Dict) -> bool:
    """Fix KFC pricing by multiplying 3-digit prices by 10"""
    if offer.get('restaurant_name') != 'KFC Iceland':
        return False
    
    price_kr = offer.get('price_kr')
    if price_kr is None:
        return False
    
    # Check if price is 3 digits (100-999)
    if 100 <= price_kr <= 999:
        old_price = price_kr
        new_price = price_kr * 10
        offer['price_kr'] = float(new_price)
        logger.info(f"Fixed KFC price: {old_price} kr -> {new_price} kr for '{offer.get('offer_name', 'Unknown')}'")
        return True
    
    return False

def fix_family_classification(offer: Dict) -> bool:
    """Fix family meal_type classification to only be family if 'fjölskyldu' appears in text"""
    if offer.get('meal_type') != 'family':
        return False
    
    offer_name = offer.get('offer_name', '').lower()
    description = offer.get('description', '').lower() if offer.get('description') else ''
    
    # Check if "fjölskyldu" appears in the text
    full_text = f"{offer_name} {description}"
    if 'fjölskyldu' in full_text:
        # This is correctly classified as family
        return False
    
    # This is incorrectly classified as family, fix it
    total_items = offer.get('total_food_items', 0)
    food_items = offer.get('food_items', [])
    main_items = offer.get('main_items', [])
    side_items = offer.get('side_items', [])
    drink_items = offer.get('drink_items', [])
    
    # Apply proper classification logic
    if len(main_items) >= 2:
        new_meal_type = 'sharing'  # Multiple main items
    elif main_items and (side_items or drink_items):
        new_meal_type = 'combo'  # Combo meal
    elif main_items:
        new_meal_type = 'individual'  # Single main item
    elif offer.get('dessert_items'):
        new_meal_type = 'dessert'  # Dessert item
    else:
        new_meal_type = 'snack'  # Side items only
    
    old_meal_type = offer['meal_type']
    offer['meal_type'] = new_meal_type
    
    # Update visual summary to reflect new meal type
    if offer.get('visual_summary'):
        # Replace family icon with appropriate icon
        meal_type_icons = {
            'family': '👨‍👩‍👧‍👦',
            'sharing': '👥',
            'combo': '🍽️',
            'individual': '🧑',
            'dessert': '🍰',
            'snack': '🥨'
        }
        
        old_icon = meal_type_icons.get('family', '👨‍👩‍👧‍👦')
        new_icon = meal_type_icons.get(new_meal_type, '🍽️')
        
        visual_summary = offer['visual_summary']
        if visual_summary.startswith(old_icon):
            offer['visual_summary'] = visual_summary.replace(old_icon, new_icon, 1)
    
    logger.info(f"Fixed meal type: '{old_meal_type}' -> '{new_meal_type}' for '{offer.get('offer_name', 'Unknown')}'")
    return True

def fix_enhanced_offers_file(file_path: str) -> None:
    """Fix issues in the enhanced offers JSON file"""
    logger.info(f"Loading enhanced offers from {file_path}")
    
    # Load the data
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    offers = data.get('offers', [])
    
    total_offers = len(offers)
    kfc_price_fixes = 0
    family_classification_fixes = 0
    
    logger.info(f"Processing {total_offers} offers...")
    
    # Fix each offer
    for offer in offers:
        # Fix KFC pricing
        if fix_kfc_pricing(offer):
            kfc_price_fixes += 1
        
        # Fix family classification
        if fix_family_classification(offer):
            family_classification_fixes += 1
    
    # Save the fixed data
    backup_path = file_path + '.backup'
    logger.info(f"Creating backup at {backup_path}")
    
    # Create backup
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Save fixed data
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Fixes applied:")
    logger.info(f"   - KFC price fixes: {kfc_price_fixes}")
    logger.info(f"   - Family classification fixes: {family_classification_fixes}")
    logger.info(f"   - Total offers processed: {total_offers}")
    logger.info(f"   - Backup saved to: {backup_path}")

def main():
    """Main function to fix data issues"""
    # Files to fix
    files_to_fix = [
        'backend/enhanced_offers_with_food_info.json',
        'scraper/enhanced_offers_with_food_info.json',
        'frontend/public/enhanced_offers_with_food_info.json'
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            logger.info(f"\n📁 Processing {file_path}")
            fix_enhanced_offers_file(file_path)
        else:
            logger.warning(f"⚠️  File not found: {file_path}")
    
    logger.info("\n🎉 All fixes completed!")

if __name__ == "__main__":
    main() 