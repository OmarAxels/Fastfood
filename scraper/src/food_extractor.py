#!/usr/bin/env python3
"""
Food Information Extractor

Extracts structured food information from offer descriptions to enable
visual representations of offers.
"""
import re
from typing import Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class FoodExtractor:
    """Extracts structured food information from offer descriptions"""
    
    def __init__(self):
        # Icelandic numbers mapping
        self.icelandic_numbers = {
            'einn': 1, 'ein': 1, 'eitt': 1,
            'tveir': 2, 'tvær': 2, 'tvö': 2,
            'þrír': 3, 'þrjár': 3, 'þrjú': 3,
            'fjórir': 4, 'fjórar': 4, 'fjögur': 4,
            'fimm': 5,
            'sex': 6,
            'sjö': 7,
            'átta': 8,
            'níu': 9,
            'tíu': 10,
            'ellefu': 11,
            'tólf': 12
        }
        
        # Food categories and their Icelandic terms
        self.food_categories = {
            'pizza': {
                'terms': ['pizza', 'pizzur', 'pizzu', 'pönnupizza'],
                'category': 'main',
                'icon': '🍕'
            },
            'burger': {
                'terms': ['hamborgari', 'borgari', 'burger', 'búlluborgari', 'búlluborgarar', 'barnaborgari', 'barnaborgarar'],
                'category': 'main', 
                'icon': '🍔'
            },
            'sub': {
                'terms': ['bátur', 'báta', 'bát', 'skinkubát', 'pizzabát', 'sub'],
                'category': 'main',
                'icon': '🥪'
            },
            'chicken': {
                'terms': ['kjúklingur', 'kjúklingabitar', 'kjúklingalundir', 'chicken', 'wings', 'hot wings'],
                'category': 'main',
                'icon': '🍗'
            },
            'fries': {
                'terms': ['franskar', 'kartöflur', 'fries'],
                'category': 'side',
                'icon': '🍟'
            },
            'soda': {
                'terms': ['gos', 'gosdrykk', 'drykkur', 'soda', 'kók', 'kóka', 'ískalt gos'],
                'category': 'drink',
                'icon': '🥤'
            },
            'cookie': {
                'terms': ['kaka', 'kökur', 'cookie', 'cookies'],
                'category': 'dessert',
                'icon': '🍪'
            },
            'sauce': {
                'terms': ['sósa', 'sósur', 'sauce', 'dip'],
                'category': 'side',
                'icon': '🍅'
            },
            'salad': {
                'terms': ['salat', 'hrásalat', 'grænmeti', 'salad'],
                'category': 'side',
                'icon': '🥗'
            },
            'fruit': {
                'terms': ['ávaxta', 'ávextir', 'fruit', 'juice'],
                'category': 'drink',
                'icon': '🧃'
            },
            'snack': {
                'terms': ['snakki', 'meðlæti', 'side', 'snack'],
                'category': 'side',
                'icon': '🥨'
            }
        }
        
        # Size patterns
        self.size_patterns = {
            'inches': r'(\d+)\s*["\']?\s*tommu?',  # 12 tommu, 6"
            'liters': r'(\d+)\s*lítra',              # 2 lítra
            'pizza_size': r'(stór|lítil|miðlungs|pönnupizza)',  # stór pizza
            'general_size': r'(stór|lítil|miðlungs|stor|lítill|big|small|large|medium)'
        }
    
    def extract_food_info(self, offer_name: str, description: str = "") -> Dict:
        """
        Extract structured food information from offer name and description
        
        Returns:
            Dict with food_items, total_items, meal_type,
        """
        full_text = f"{offer_name} {description}".lower()
        
        # Extract food items with quantities and sizes
        food_items = self._extract_food_items(full_text)
        
        # Determine meal type and complexity
        meal_type = self._determine_meal_type(food_items)

        
        # Extract total item count
        total_items = sum(item.get('quantity', 1) for item in food_items)
        
        # Determine if it's a combo meal
        is_combo = len([item for item in food_items if item['category'] in ['main', 'side', 'drink']]) >= 2
        
        result = {
            'food_items': food_items,
            'total_items': total_items,
            'meal_type': meal_type,
            'is_combo': is_combo,
 
            'main_items': [item for item in food_items if item['category'] == 'main'],
            'side_items': [item for item in food_items if item['category'] == 'side'],
            'drink_items': [item for item in food_items if item['category'] == 'drink'],
            'dessert_items': [item for item in food_items if item['category'] == 'dessert']
        }
        
        return result
    
    def _extract_food_items(self, text: str) -> List[Dict]:
        """Extract individual food items with quantities and sizes"""
        items = []
        
        # Split text into potential food phrases
        phrases = re.split(r'[,\.\|]|og|með|ásamt|fyrir', text)
        
        for phrase in phrases:
            phrase = phrase.strip()
            if len(phrase) < 3:  # Skip very short phrases
                continue
                
            # Look for each food category
            for food_type, config in self.food_categories.items():
                for term in config['terms']:
                    if term in phrase:
                        item = self._extract_item_details(phrase, food_type, term, config)
                        if item:
                            items.append(item)
                            break
        
        # Remove duplicates and merge similar items
        items = self._merge_similar_items(items)
        
        return items
    
    def _extract_item_details(self, phrase: str, food_type: str, matched_term: str, config: Dict) -> Optional[Dict]:
        """Extract quantity, size and other details for a specific food item"""
        
        # Extract quantity
        quantity = self._extract_quantity(phrase, matched_term)
        
        # Extract size information
        size_info = self._extract_size(phrase)
        
        # Extract any special modifiers
        modifiers = self._extract_modifiers(phrase, food_type)
        
        item = {
            'type': food_type,
            'name': matched_term,
            'category': config['category'],
            'icon': config['icon'],
            'quantity': quantity,
            'size': size_info,
            'modifiers': modifiers,
            'phrase': phrase.strip()
        }
        
        return item
    
    def _extract_quantity(self, phrase: str, term: str) -> int:
        """Extract quantity from phrase"""
        
        # Look for explicit numbers before the food term
        number_before = re.search(r'(\d+)\s*.*?' + re.escape(term), phrase)
        if number_before:
            return int(number_before.group(1))
        
        # Look for Icelandic number words
        for icelandic_num, value in self.icelandic_numbers.items():
            if icelandic_num in phrase:
                return value
        
        # Default to 1 if no quantity found
        return 1
    
    def _extract_size(self, phrase: str) -> Optional[Dict]:
        """Extract size information from phrase"""
        size_info = {}
        
        # Check for inches
        inches_match = re.search(self.size_patterns['inches'], phrase)
        if inches_match:
            size_info['inches'] = int(inches_match.group(1))
            size_info['unit'] = 'inches'
        
        # Check for liters
        liters_match = re.search(self.size_patterns['liters'], phrase)
        if liters_match:
            size_info['liters'] = int(liters_match.group(1))
            size_info['unit'] = 'liters'
        
        # Check for pizza size descriptors
        pizza_size_match = re.search(self.size_patterns['pizza_size'], phrase)
        if pizza_size_match:
            size_info['descriptor'] = pizza_size_match.group(1)
            size_info['unit'] = 'descriptor'
        
        # Check for general size descriptors
        general_size_match = re.search(self.size_patterns['general_size'], phrase)
        if general_size_match and 'descriptor' not in size_info:
            size_info['descriptor'] = general_size_match.group(1)
            size_info['unit'] = 'descriptor'
        
        return size_info if size_info else None
    
    def _extract_modifiers(self, phrase: str, food_type: str) -> List[str]:
        """Extract modifiers like flavors, preparations, etc."""
        modifiers = []
        
        # Common modifiers by food type
        modifier_patterns = {
            'pizza': ['stór', 'lítil', 'pönnupizza', 'margarita', 'pepperoni'],
            'chicken': ['original', 'zinger', 'hot', 'spicy', 'heit'],
            'sauce': ['heit', 'brún', 'bbq', 'kokteilsósa', 'hot sauce'],
            'sub': ['skinkubát', 'pizzabát', 'kalkún', 'túnfisk', 'grænmetissælu']
        }
        
        if food_type in modifier_patterns:
            for modifier in modifier_patterns[food_type]:
                if modifier in phrase:
                    modifiers.append(modifier)
        
        return modifiers
    
    def _merge_similar_items(self, items: List[Dict]) -> List[Dict]:
        """Merge similar food items and combine quantities"""
        merged = []
        
        for item in items:
            # Check if we already have a similar item
            existing = None
            for merged_item in merged:
                if (merged_item['type'] == item['type'] and 
                    merged_item.get('size') == item.get('size')):
                    existing = merged_item
                    break
            
            if existing:
                # Merge quantities
                existing['quantity'] += item['quantity']
                # Combine modifiers
                if item['modifiers']:
                    existing['modifiers'].extend(item['modifiers'])
                    existing['modifiers'] = list(set(existing['modifiers']))  # Remove duplicates
            else:
                merged.append(item)
        
        return merged
    
    def _determine_meal_type(self, food_items: List[Dict]) -> str:
        """Determine the type of meal based on food items"""
        categories = [item['category'] for item in food_items]
        total_items = sum(item['quantity'] for item in food_items)
        
        if total_items >= 6:
            return 'family'  # Family meal
        elif len([c for c in categories if c == 'main']) >= 2:
            return 'sharing'  # Multiple main items
        elif 'main' in categories and ('side' in categories or 'drink' in categories):
            return 'combo'  # Combo meal
        elif 'main' in categories:
            return 'individual'  # Single main item
        elif 'dessert' in categories:
            return 'dessert'  # Dessert item
        else:
            return 'snack'  # Side items only

  