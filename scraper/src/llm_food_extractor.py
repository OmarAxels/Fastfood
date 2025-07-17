#!/usr/bin/env python3
"""
LLM-based Food Information Extractor

Uses LLM via g4f to extract structured food information from offer descriptions.
"""
import json
import re
import logging
from typing import Dict, List, Optional, Union
import g4f

logger = logging.getLogger(__name__)

class LLMFoodExtractor:
    """Extracts structured food information using LLM"""
    
    def __init__(self, categories_file: str = "food_categories.json"):
        """Initialize the LLM food extractor"""
        self.categories_file = categories_file
        self.categories_data = self._load_categories()
        
        # Icelandic numbers mapping
        self.icelandic_numbers = {
            'einn': 1, 'ein': 1, 'eitt': 1,
            'tveir': 2, 'tvær': 2, 'tvö': 2,
            'þrír': 3, 'þrjár': 3, 'þrjú': 3,
            'fjórir': 4, 'fjórar': 4, 'fjögur': 4,
            'fimm': 5, 'sex': 6, 'sjö': 7, 'átta': 8, 'níu': 9, 'tíu': 10,
            'ellefu': 11, 'tólf': 12
        }
        
        # Icelandic declension normalization mapping
        self.icelandic_declensions = {
            # Beverages (soda)
            'gosi': 'gos',
            'gosinu': 'gos',
            'goss': 'gos',
            'gosanna': 'gos',
            'gosum': 'gos',
            
            # Fries
            'frönskum': 'franskar',
            'franska': 'franskar',
            'franskar': 'franskar',
            'franskum': 'franskar',
            'frönsku': 'franskar',
            
            # Burgers
            'borgara': 'borgari',
            'borgarann': 'borgari',
            'borgaranum': 'borgari',
            'borgarans': 'borgari',
            'borgari': 'borgari',
            'borgurum': 'borgari',
            
            # Chicken
            'kjúklinginn': 'kjúklingur',
            'kjúklingnum': 'kjúklingur',
            'kjúklings': 'kjúklingur',
            'kjúklinga': 'kjúklingur',
            'kjúklingum': 'kjúklingur',
            'kjúklingunum': 'kjúklingur',
            
            # Pizza
            'pizzuna': 'pizza',
            'pizzunni': 'pizza',
            'pizzunnar': 'pizza',
            'pizzur': 'pizza',
            'pizzum': 'pizza',
            'pizzanna': 'pizza',
            
            # Wings
            'vængina': 'vængir',
            'væng': 'vængir',
            'vængjum': 'vængir',
            'vængina': 'vængir',
            
            # Sauce
            'sósu': 'sósa',
            'sósunni': 'sósa',
            'sósur': 'sósa',
            'sósum': 'sósa',
            'sósanna': 'sósa',
            
            # Bread/sub
            'brauðinu': 'brauð',
            'brauðs': 'brauð',
            'brauðið': 'brauð',
            'báti': 'bátur',
            'bátinn': 'bátur',
            'bátnum': 'bátur',
            'báta': 'bátur',
            'bátum': 'bátur',
        }
        
        # Size patterns
        self.size_patterns = {
            'inches': r'(\d+)\s*["\']?\s*tommu?',  # 12 tommu, 6"
            'liters': r'(\d+)\s*lítra',              # 2 lítra
            'pizza_size': r'(stór|lítil|miðlungs|pönnupizza)',  # stór pizza
            'general_size': r'(stór|lítil|miðlungs|stor|lítill|big|small|large|medium)'
        }
    
    def _load_categories(self) -> Dict:
        """Load food categories from JSON file"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Categories file {self.categories_file} not found")
            return {"food_categories": {}, "categories": {}, "meal_types": {}}
    
    def _save_categories(self):
        """Save updated categories back to JSON file"""
        try:
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Updated categories saved to {self.categories_file}")
        except Exception as e:
            logger.error(f"Failed to save categories: {e}")
    
    def extract_food_info_batch(self, offers: List[Dict]) -> List[Dict]:
        """Extract food information for a batch of offers from the same restaurant"""
        if not offers:
            return []
        
        restaurant_name = offers[0].get('restaurant_name', 'Unknown')
        logger.info(f"Processing {len(offers)} offers from {restaurant_name}")
        
        # Prepare batch data for LLM
        batch_data = []
        for offer in offers:
            batch_data.append({
                'offer_name': offer.get('offer_name', ''),
                'description': offer.get('description', ''),
                'price_kr': offer.get('price_kr'),
                'available_weekdays': offer.get('available_weekdays'),
                'available_hours': offer.get('available_hours'),
                'pickup_delivery': offer.get('pickup_delivery'),
                'suits_people': offer.get('suits_people')
            })
        
        # Process with LLM
        enhanced_offers = []
        for i, offer in enumerate(offers):
            try:
                enhanced_offer = offer.copy()
                food_info = self._extract_single_offer_food_info(offer, batch_data[i])
                enhanced_offer.update(food_info)
                enhanced_offers.append(enhanced_offer)
            except Exception as e:
                logger.error(f"Failed to process offer {i}: {e}")
                # Add empty food info on failure
                enhanced_offer = offer.copy()
                enhanced_offer.update(self._get_empty_food_info())
                enhanced_offers.append(enhanced_offer)
        
        return enhanced_offers
    
    def _extract_single_offer_food_info(self, offer: Dict, batch_data: Dict) -> Dict:
        """Extract food information for a single offer using LLM"""
        
        # Prepare prompt for LLM
        prompt = self._create_llm_prompt(offer, batch_data)
        
        try:
            # Get LLM response
            response = g4f.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            # Parse LLM response
            food_info = self._parse_llm_response(response, offer)
            
            # Update categories if new food types were found
            if food_info.get('new_categories'):
                self._update_categories(food_info['new_categories'])
            
            return food_info
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._get_empty_food_info()
    
    def _create_llm_prompt(self, offer: Dict, batch_data: Dict) -> str:
        """Create prompt for LLM"""
        # Debug output to stderr instead of stdout
        import sys
        print(f"Creating prompt for offer: {offer['offer_name']}", file=sys.stderr)

        # Get current food categories
        food_categories = self.categories_data['food_categories']
        categories = self.categories_data['categories']
        meal_types = self.categories_data['meal_types']
        
        # Build category descriptions
        food_categories_text = "\n".join([
            f"- {cat_name}: {cat_data['description']} (category: {cat_data['category']})"
            for cat_name, cat_data in food_categories.items()
        ])
        
        categories_text = "\n".join([
            f"- {cat_name}: {cat_data['description']}"
            for cat_name, cat_data in categories.items()
        ])
        
        meal_types_text = "\n".join([
            f"- {meal_name}: {meal_data['description']}"
            for meal_name, meal_data in meal_types.items()
        ])
        
        prompt = f"""
You are a food categorization expert specializing in Icelandic restaurant offers. Analyze the following restaurant offer and extract structured food information.

IMPORTANT INSTRUCTIONS:

1. ICELANDIC DECLENSIONS: Normalize Icelandic words to their base form:
   - "gosi", "gosinu", "goss" → "gos" (soda)
   - "frönskum", "franska", "frönsku" → "franskar" (fries)
   - "borgara", "borgarann" → "borgari" (burger)
   - "kjúklinga", "kjúklingnum" → "kjúklingur" (chicken)
   - "pizzuna", "pizzunni" → "pizza"
   - "sósu", "sósunni" → "sósa" (sauce)
   - Always use the nominative singular form for food names

2. FOOD CHOICES: When you see "eða" (or), treat as alternatives/choices:
   - "gos eða djús" = customer can choose soda OR juice
   - Create separate entries for each choice item
   - Mark ALL choice items with "is_choice": true
   - Use "choice_group" to link alternatives (e.g., "drinks")

3. FOOD CATEGORIZATION: Use these categories accurately:
   - burger: Any type of burger (borgari, hamborgari, etc.)
   - fries: French fries (franskar, frönskum, etc.)
   - soda: Carbonated drinks (gos, kók, etc.)
   - fruit: Juice and fruit drinks (djús, appelsínusafi, etc.)
   - chicken: Chicken items (kjúklingur, wings, etc.)
   - pizza: Pizza items
   - sauce: Dipping sauces and condiments
   - salad: Salads and vegetables

EXAMPLE:
"Barnaborgari með frönskum og gosi eða djús" should be parsed as:
- barnaborgari (burger, not a choice)
- franskar (fries, not a choice)  
- gos (soda, is_choice: true, choice_group: "drinks")
- djús (fruit, is_choice: true, choice_group: "drinks")

AVAILABLE FOOD CATEGORIES:
{food_categories_text}

AVAILABLE CATEGORIES:
{categories_text}

AVAILABLE MEAL TYPES:
{meal_types_text}

RESTAURANT OFFER TO ANALYZE:
Title: {batch_data['offer_name']}
Description: {batch_data['description']}
Price: {batch_data['price_kr']} kr
Available Weekdays: {batch_data['available_weekdays']}
Available Hours: {batch_data['available_hours']}
Pickup/Delivery: {batch_data['pickup_delivery']}
Suits People: {batch_data['suits_people']}

RESPONSE FORMAT (JSON):
{{
  "food_items": [
    {{
      "name": "normalized_base_form_name",
      "type": "category_name",
      "quantity": number,
      "size": {{"descriptor": "size_desc"}} or null,
      "modifiers": ["modifier1", "modifier2"],
      "is_choice": true/false,
      "choice_group": "group_name" or null
    }}
  ],
  "meal_type": "meal_type_name",
  "is_combo": true/false,
  "complexity_score": number,
  "total_items": number,
  "additional_info": {{
    "weekdays": "extracted weekdays",
    "hours": "extracted hours", 
    "pickup_delivery": "extracted pickup/delivery info"
  }},
  "new_categories": [
    {{
      "name": "new_category_name",
      "description": "description of the new category",
      "category": "main/side/drink/dessert"
    }}
  ]
}}

Respond only with valid JSON. If no food items are found, return empty arrays for food_items and new_categories.
"""
        
        return prompt
    
    def _parse_llm_response(self, response: str, offer: Dict) -> Dict:
        """Parse LLM response and convert to food info format"""
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in LLM response")
                return self._get_empty_food_info()
            
            llm_data = json.loads(json_match.group())
            
            # Convert to our format
            food_items = []
            for item in llm_data.get('food_items', []):
                # Normalize Icelandic declensions
                normalized_name = self._normalize_icelandic_word(item['name'])
                
                # Handle choices using choice_group
                is_choice = item.get('is_choice', False)
                choice_group = item.get('choice_group')
                
                # Create food item
                food_item = {
                    'type': item['type'],
                    'name': normalized_name,
                    'category': self._get_category_for_type(item['type']),
                    'icon': self._get_icon_for_type(item['type']),
                    'quantity': item.get('quantity', 1),
                    'size': item.get('size'),
                    'modifiers': item.get('modifiers', []),
                    'phrase': f"{item.get('quantity', 1)} {normalized_name}",
                    'is_choice': is_choice,
                    'choice_group': choice_group
                }
                food_items.append(food_item)
                
            # Calculate complexity and determine meal type
            complexity_score = self._calculate_complexity(food_items)
            meal_type = llm_data.get('meal_type', 'snack')
            
            # Count total items (don't double-count choices)
            total_items = sum(item['quantity'] for item in food_items if not item.get('is_choice', False))
            is_combo = len([item for item in food_items if item['category'] in ['main', 'side', 'drink'] and not item.get('is_choice', False)]) >= 2
            
            # Group items by category
            main_items = [item for item in food_items if item['category'] == 'main']
            side_items = [item for item in food_items if item['category'] == 'side']
            drink_items = [item for item in food_items if item['category'] == 'drink']
            dessert_items = [item for item in food_items if item['category'] == 'dessert']
            
            return {
                'food_items': food_items,
                'meal_type': meal_type,
                'is_combo': is_combo,
                'complexity_score': complexity_score,
                'total_food_items': total_items,
                'main_items': main_items,
                'side_items': side_items,
                'drink_items': drink_items,
                'dessert_items': dessert_items,
                'visual_summary': self._get_visual_summary(food_items, meal_type),
                'new_categories': llm_data.get('new_categories', [])
            }
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._get_empty_food_info()
    
    def _normalize_icelandic_word(self, word: str) -> str:
        """Normalize Icelandic word using declension mapping"""
        if not word:
            return word
        
        word_lower = word.lower().strip()
        return self.icelandic_declensions.get(word_lower, word)
    
    def _guess_food_type(self, word: str) -> str:
        """Guess food type for alternative items"""
        word_lower = word.lower()
        
        # Common mappings for alternatives
        if any(x in word_lower for x in ['gos', 'kók', 'pepsi', 'sprite']):
            return 'soda'
        elif any(x in word_lower for x in ['djús', 'safi', 'appelsínu']):
            return 'fruit'
        elif any(x in word_lower for x in ['franskar', 'frönskum']):
            return 'fries'
        elif any(x in word_lower for x in ['borgari', 'burger']):
            return 'burger'
        elif any(x in word_lower for x in ['kjúkling', 'chicken', 'wings']):
            return 'chicken'
        elif any(x in word_lower for x in ['pizza']):
            return 'pizza'
        elif any(x in word_lower for x in ['sósa', 'sauce']):
            return 'sauce'
        else:
            # Try to find it in food categories
            food_categories = self.categories_data.get('food_categories', {})
            for cat_name, cat_data in food_categories.items():
                terms = cat_data.get('terms', [])
                if any(term in word_lower for term in terms):
                    return cat_name
            
            return 'snack'  # Default fallback
    
    def _get_category_for_type(self, food_type: str) -> str:
        """Get category for a food type"""
        food_categories = self.categories_data['food_categories']
        if food_type in food_categories:
            return food_categories[food_type]['category']
        return 'main'  # Default to main
    
    def _get_icon_for_type(self, food_type: str) -> str:
        """Get icon for a food type"""
        food_categories = self.categories_data['food_categories']
        if food_type in food_categories:
            return food_categories[food_type]['icon']
        return 'mdi:food'  # Default icon
    
    def _update_categories(self, new_categories: List[Dict]):
        """Update categories file with new categories"""
        for new_cat in new_categories:
            cat_name = new_cat['name']
            if cat_name not in self.categories_data['food_categories']:
                self.categories_data['food_categories'][cat_name] = {
                    'terms': [cat_name],
                    'category': new_cat['category'],
                    'icon': '',  # Leave blank for human to decide
                    'description': new_cat['description']
                }
                logger.info(f"Added new category: {cat_name}")
        
        # Save updated categories
        self._save_categories()
    
    def _calculate_complexity(self, food_items: List[Dict]) -> int:
        """Calculate complexity score based on variety and quantity"""
        if not food_items:
            return 0
        
        # Base score from number of items
        total_quantity = sum(item['quantity'] for item in food_items)
        complexity = min(total_quantity, 10)  # Cap at 10
        
        # Add points for variety
        unique_types = len(set(item['type'] for item in food_items))
        complexity += unique_types * 2
        
        # Add points for different categories
        unique_categories = len(set(item['category'] for item in food_items))
        complexity += unique_categories
        
        # Add points for size specifications
        has_sizes = any(item.get('size') for item in food_items)
        if has_sizes:
            complexity += 2
        
        return min(complexity, 20)  # Cap at 20
    
    def _get_visual_summary(self, food_items: List[Dict], meal_type: str) -> str:
        """Generate a visual summary string for the offer"""
        if not food_items:
            return "🍽️ General offer"
        
        # Filter out choice items to avoid duplicates in visual summary
        main_items = [item for item in food_items if not item.get('is_choice', False)]
        
        # Group by category
        main_icons = [item['icon'] for item in main_items if item['category'] == 'main']
        side_icons = [item['icon'] for item in main_items if item['category'] == 'side']
        drink_icons = [item['icon'] for item in main_items if item['category'] == 'drink']
        dessert_icons = [item['icon'] for item in main_items if item['category'] == 'dessert']
        
        # Create visual string
        visual_parts = []
        if main_icons:
            visual_parts.append(''.join(main_icons))
        if side_icons:
            visual_parts.append(''.join(side_icons))
        if drink_icons:
            visual_parts.append(''.join(drink_icons))
        if dessert_icons:
            visual_parts.append(''.join(dessert_icons))
        
        visual = ' + '.join(visual_parts) if visual_parts else "🍽️"
        
        # Add meal type indicator
        meal_type_icons = {
            'family': '👨‍👩‍👧‍👦',
            'sharing': '👥',
            'combo': '🍽️',
            'individual': '🧑',
            'dessert': '🍰',
            'snack': '🥨'
        }
        
        type_icon = meal_type_icons.get(meal_type, '🍽️')
        
        return f"{type_icon} {visual}"
    
    def _get_empty_food_info(self) -> Dict:
        """Return empty food info structure"""
        return {
            'food_items': [],
            'meal_type': 'unknown',
            'is_combo': False,
            'complexity_score': 0,
            'total_food_items': 0,
            'main_items': [],
            'side_items': [],
            'drink_items': [],
            'dessert_items': [],
            'visual_summary': '🍽️ General offer'
        } 