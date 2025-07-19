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
from pathlib import Path
import json as _json

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
        
        # Process all offers in a single LLM call for better context
        try:
            enhanced_offers = self._extract_batch_food_info(offers)
            return enhanced_offers
        except Exception as e:
            logger.error(f"Batch processing failed, falling back to individual processing: {e}")
            # Fallback to individual processing
            return self._extract_individual_offers(offers)
    
    def _extract_batch_food_info(self, offers: List[Dict]) -> List[Dict]:
        """Extract food information for all offers in a single LLM call"""
        
        # Prepare batch data for LLM
        batch_data = []
        for i, offer in enumerate(offers):
            batch_data.append({
                'id': i + 1,
                'offer_name': offer.get('offer_name', ''),
                'description': offer.get('description', ''),
                'price_kr': offer.get('price_kr'),
                'available_weekdays': offer.get('available_weekdays'),
                'available_hours': offer.get('available_hours'),
                'pickup_delivery': offer.get('pickup_delivery'),
                'suits_people': offer.get('suits_people')
            })
        
        # Create prompt for batch processing
        prompt = self._create_batch_llm_prompt(batch_data)
        
        try:
            # Get LLM response for all offers
            response = g4f.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            # Parse batch response
            batch_results = self._parse_batch_llm_response(response, offers)
            
            # Update categories if new food types were found
            for result in batch_results:
                if result.get('new_categories'):
                    self._update_categories(result['new_categories'])
            
            return batch_results
            
        except Exception as e:
            logger.error(f"Batch LLM extraction failed: {e}")
            # Return empty food info for all offers
            return [self._get_empty_food_info() for _ in offers]
    
    def _extract_individual_offers(self, offers: List[Dict]) -> List[Dict]:
        """Fallback: Extract food information for offers individually"""
        enhanced_offers = []
        for i, offer in enumerate(offers):
            try:
                enhanced_offer = offer.copy()
                food_info = self._extract_single_offer_food_info(offer, offer)
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
   - djús: Juice and fruit drinks (djús, appelsínusafi, etc.)
   - chicken: Chicken items (kjúklingur, wings, etc.)
   - pizza: Pizza items
   - sauce: Dipping sauces and condiments
   - salad: Salads and vegetables

4. SIZE PARSING: Pay attention to size specifications:
   - "2 l gos" = 1 soda with size: {{"liters": 2}} (NOT 2 sodas)
   - "stór franskar" = 1 fries with size: {{"descriptor": "stór"}}
   - "12 tommu pizza" = 1 pizza with size: {{"inches": 12}}
   - Always separate quantity from size information

EXAMPLE:
"Barnaborgari með frönskum og gosi eða djús" should be parsed as:
- barnaborgari (burger, not a choice)
- franskar (fries, not a choice)  
- gos (soda, is_choice: true, choice_group: "drinks")
- djús (djús, is_choice: true, choice_group: "drinks")

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

                # Normalize soda quantity when size in liters implied by quantity (e.g., "2 l gos")
                if food_item['type'] == 'soda':
                    if food_item.get('size') and food_item['size'].get('liters'):
                        food_item['quantity'] = 1
                        food_item['phrase'] = f"1 {food_item['name']}"
                    elif food_item['quantity'] > 1 and not food_item.get('size'):
                        # Assume quantity represents liters if >1 and <=3
                        if 1 < food_item['quantity'] <= 3:
                            food_item['size'] = { 'liters': food_item['quantity'] }
                            food_item['quantity'] = 1
                            food_item['phrase'] = f"1 {food_item['size']['liters']}L {food_item['name']}"

                food_items.append(food_item)
                
            # Calculate complexity and determine meal type
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
                'total_food_items': total_items,
                'main_items': main_items,
                'side_items': side_items,
                'drink_items': drink_items,
                'dessert_items': dessert_items,
                'new_categories': llm_data.get('new_categories', [])
            }
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._get_empty_food_info()
    
    def _create_batch_llm_prompt(self, batch_data: List[Dict]) -> str:
        """Create prompt for batch LLM processing"""
        # Debug output to stderr instead of stdout
        import sys
        print(f"Creating batch prompt for {len(batch_data)} offers", file=sys.stderr)

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
        
        # Build offers list
        offers_text = "\n\n".join([
            f"OFFER {data['id']}:\n"
            f"Title: {data['offer_name']}\n"
            f"Description: {data['description']}\n"
            f"Price: {data['price_kr']} kr\n"
            f"Available Weekdays: {data['available_weekdays']}\n"
            f"Available Hours: {data['available_hours']}\n"
            f"Pickup/Delivery: {data['pickup_delivery']}\n"
            f"Suits People: {data['suits_people']}"
            for data in batch_data
        ])
        
        prompt = f"""
You are a food categorization expert specializing in Icelandic restaurant offers. Analyze the following batch of restaurant offers and extract structured food information for each one.

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

4. BATCH PROCESSING: Process ALL offers in the batch. Use the offer ID to match responses.

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

RESTAURANT OFFERS TO ANALYZE:
{offers_text}

RESPONSE FORMAT (JSON):
{{
  "offers": [
    {{
      "offer_id": 1,
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
  ]
}}

Respond only with valid JSON. If no food items are found for an offer, return empty arrays for food_items and new_categories for that offer.
"""
        
        return prompt
    
    def _parse_batch_llm_response(self, response: str, offers: List[Dict]) -> List[Dict]:
        """Parse batch LLM response and convert to food info format"""
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in batch LLM response")
                return [self._get_empty_food_info() for _ in offers]
            
            llm_data = json.loads(json_match.group())
            
            # Create results array
            results = []
            
            # Process each offer result
            for offer_result in llm_data.get('offers', []):
                offer_id = offer_result.get('offer_id', 1)
                offer_index = offer_id - 1  # Convert to 0-based index
                
                # Ensure we have a valid index
                if offer_index >= len(offers):
                    logger.warning(f"Offer ID {offer_id} out of range, skipping")
                    continue
                
                # Convert to our format
                food_items = []
                for item in offer_result.get('food_items', []):
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

                    # Normalize soda quantity when size in liters implied by quantity (e.g., "2 l gos")
                    if food_item['type'] == 'soda':
                        if food_item.get('size') and food_item['size'].get('liters'):
                            food_item['quantity'] = 1
                            food_item['phrase'] = f"1 {food_item['name']}"
                        elif food_item['quantity'] > 1 and not food_item.get('size'):
                            # Assume quantity represents liters if >1 and <=3
                            if 1 < food_item['quantity'] <= 3:
                                food_item['size'] = { 'liters': food_item['quantity'] }
                                food_item['quantity'] = 1
                                food_item['phrase'] = f"1 {food_item['size']['liters']}L {food_item['name']}"

                    food_items.append(food_item)
                    
                # Calculate complexity and determine meal type
                meal_type = offer_result.get('meal_type', 'snack')
                
                # Count total items (don't double-count choices)
                total_items = sum(item['quantity'] for item in food_items if not item.get('is_choice', False))
                is_combo = len([item for item in food_items if item['category'] in ['main', 'side', 'drink'] and not item.get('is_choice', False)]) >= 2
                
                # Group items by category
                main_items = [item for item in food_items if item['category'] == 'main']
                side_items = [item for item in food_items if item['category'] == 'side']
                drink_items = [item for item in food_items if item['category'] == 'drink']
                dessert_items = [item for item in food_items if item['category'] == 'dessert']
                
                result = {
                    'food_items': food_items,
                    'meal_type': meal_type,
                    'is_combo': is_combo,
                    'total_food_items': total_items,
                    'main_items': main_items,
                    'side_items': side_items,
                    'drink_items': drink_items,
                    'dessert_items': dessert_items,
                    'new_categories': offer_result.get('new_categories', [])
                }
                
                results.append(result)
            
            # Ensure we have results for all offers
            while len(results) < len(offers):
                results.append(self._get_empty_food_info())
            
            return results[:len(offers)]  # Ensure we don't return more than expected
            
        except Exception as e:
            logger.error(f"Failed to parse batch LLM response: {e}")
            return [self._get_empty_food_info() for _ in offers]
    
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
            return 'juice'
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
        if food_type in food_categories and food_categories[food_type].get('icon'):
            return food_categories[food_type]['icon']

        # Fallback to central icon mapping JSON
        try:
            icon_map_path = Path(__file__).resolve().parent.parent / 'food_icon_mapping.json'
            if not hasattr(self, '_icon_map_cache'):
                if icon_map_path.exists():
                    with open(icon_map_path, 'r', encoding='utf-8') as f:
                        self._icon_map_cache = _json.load(f)
                else:
                    self._icon_map_cache = {}
            icon_mapping = self._icon_map_cache
            if food_type in icon_mapping and icon_mapping[food_type].get('icon'):
                return icon_mapping[food_type]['icon']
        except Exception as e:
            logger.error(f"Failed loading icon mapping: {e}")

        return 'mdi:food'  # Default icon
    
    def _update_categories(self, new_categories: List[Dict]):
        """Update categories file with new categories and sync icon mapping json"""
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

        # --- NEW: Update central icon mapping JSON ---
        try:
            icon_map_path = Path(__file__).resolve().parent.parent / 'food_icon_mapping.json'
            if icon_map_path.exists():
                with open(icon_map_path, 'r', encoding='utf-8') as f:
                    icon_map = _json.load(f)
            else:
                icon_map = {}
            updated = False
            for new_cat in new_categories:
                name = new_cat['name']
                if name not in icon_map:
                    icon_map[name] = {"icon": "", "color": ""}
                    updated = True
            if updated:
                with open(icon_map_path, 'w', encoding='utf-8') as f:
                    _json.dump(icon_map, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to update icon mapping json: {e}")

   
    
    def _get_empty_food_info(self) -> Dict:
        """Return empty food info structure"""
        return {
            'food_items': [],
            'meal_type': 'unknown',
            'is_combo': False,
            'total_food_items': 0,
            'main_items': [],
            'side_items': [],
            'drink_items': [],
            'dessert_items': [],
        } 