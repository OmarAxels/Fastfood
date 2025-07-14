import json

# Read the backend file
with open('backend/enhanced_offers_with_food_info.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Processing {len(data['offers'])} offers...")

kfc_fixes = 0
family_fixes = 0

for offer in data['offers']:
    # Fix KFC pricing
    if (offer.get('restaurant_name') == 'KFC Iceland' and 
        offer.get('price_kr') is not None and 
        100 <= offer['price_kr'] <= 999):
        old_price = offer['price_kr']
        offer['price_kr'] = old_price * 10
        print(f"Fixed KFC price: {old_price} -> {offer['price_kr']} for '{offer['offer_name']}'")
        kfc_fixes += 1
    
    # Fix family classification
    if offer.get('meal_type') == 'family':
        offer_name = offer.get('offer_name', '').lower()
        description = offer.get('description', '').lower() if offer.get('description') else ''
        full_text = f"{offer_name} {description}"
        
        if 'fjölskyldu' not in full_text:
            # This is incorrectly classified as family
            main_items = offer.get('main_items', [])
            side_items = offer.get('side_items', [])
            drink_items = offer.get('drink_items', [])
            
            # Apply proper classification
            if len(main_items) >= 2:
                new_meal_type = 'sharing'
            elif main_items and (side_items or drink_items):
                new_meal_type = 'combo'
            elif main_items:
                new_meal_type = 'individual'
            elif offer.get('dessert_items'):
                new_meal_type = 'dessert'
            else:
                new_meal_type = 'snack'
            
            offer['meal_type'] = new_meal_type
            
            # Fix visual summary
            if offer.get('visual_summary', '').startswith('👨‍👩‍👧‍👦'):
                meal_type_icons = {
                    'sharing': '👥',
                    'combo': '🍽️',
                    'individual': '🧑',
                    'dessert': '🍰',
                    'snack': '🥨'
                }
                new_icon = meal_type_icons.get(new_meal_type, '🍽️')
                offer['visual_summary'] = offer['visual_summary'].replace('👨‍👩‍👧‍👦', new_icon, 1)
            
            print(f"Fixed meal type: family -> {new_meal_type} for '{offer['offer_name']}'")
            family_fixes += 1

# Create backup
with open('backend/enhanced_offers_with_food_info.json.backup', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Save fixed data
with open('backend/enhanced_offers_with_food_info.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nFixes completed:")
print(f"- KFC price fixes: {kfc_fixes}")
print(f"- Family classification fixes: {family_fixes}")
print("- Backup saved to: backend/enhanced_offers_with_food_info.json.backup") 