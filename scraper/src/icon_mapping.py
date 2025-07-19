"""
Icon Mapping System for Fastfood Scraper
Handles all icon assignments and data processing logic
"""

from typing import Dict, List, Any, Optional
import re
import json
from pathlib import Path


class IconMapping:
    """Centralized icon mapping system for the scraper"""
    
    # Food Type Icons with colors
    FOOD_ICONS = {
        # Meat Types
        'chicken': {'icon': 'mdi:food-drumstick', 'color': '#D4AF37'},
        'wings': {'icon': 'mdi:food-drumstick', 'color': '#D4AF37'},
        'breast': {'icon': 'mdi:food-drumstick', 'color': '#D4AF37'},
        'kjúklingur': {'icon': 'mdi:food-drumstick', 'color': '#D4AF37'},
        'kjúkling': {'icon': 'mdi:food-drumstick', 'color': '#D4AF37'},
        
        'beef': {'icon': 'mdi:food-steak', 'color': '#8B4513'},
        'nautakjöt': {'icon': 'mdi:food-steak', 'color': '#8B4513'},
        'steak': {'icon': 'mdi:food-steak', 'color': '#8B4513'},
        
        # Fast Food
        'burger': {'icon': 'fluent-emoji:hamburger', 'color': '#8B4513'},
        'pizza': {'icon': 'twemoji:pizza', 'color': '#FF6B35'},
        'sub': {'icon': 'mdi:food-sandwich', 'color': '#228B22'},
        'bátur': {'icon': 'mdi:food-sandwich', 'color': '#228B22'},
        'sandwich': {'icon': 'mdi:food-hot-dog', 'color': '#228B22'},
        'hotdog': {'icon': 'mdi:food-hot-dog', 'color': '#8B4513'},
        'wrap': {'icon': 'mdi:food-hot-dog', 'color': '#228B22'},
        'panini': {'icon': 'mdi:food-hot-dog', 'color': '#228B22'},
        
        # Sides
        'franskar': {'icon': 'mdi:food-french-fries', 'color': '#8B4513'},
        'pommes': {'icon': 'mdi:food-french-fries', 'color': '#8B4513'},
        'fries': {'icon': 'mdi:food-french-fries', 'color': '#8B4513'},
        'potato': {'icon': 'mdi:food-french-fries', 'color': '#8B4513'},
        'kartöflur': {'icon': 'mdi:food-french-fries', 'color': '#8B4513'},
        'rice': {'icon': 'mdi:rice', 'color': '#F4A460'},
        'hrísgrjón': {'icon': 'mdi:rice', 'color': '#F4A460'},
        'salad': {'icon': 'noto:green-salad', 'color': '#228B22'},
        'salat': {'icon': 'noto:green-salad', 'color': '#228B22'},
        'grænmeti': {'icon': 'mdi:food-apple', 'color': '#228B22'},
        'vegetables': {'icon': 'mdi:food-apple', 'color': '#228B22'},
        
        # Drinks
        'drykkur': {'icon': 'mdi:cup', 'color': '#4A90E2'},
        'gos': {'icon': 'mdi:cup', 'color': '#000000'},
        'soda': {'icon': 'mdi:bottle-soda-classic', 'color': '#4A90E2'},
        'kók': {'icon': 'mdi:bottle-soda-classic', 'color': '#8B0000'},
        'pepsi': {'icon': 'mdi:bottle-soda-classic', 'color': '#0066CC'},
        'cola': {'icon': 'mdi:bottle-soda-classic', 'color': '#8B0000'},
        'water': {'icon': 'mdi:cup-water', 'color': '#87CEEB'},
        'vatn': {'icon': 'mdi:cup-water', 'color': '#87CEEB'},
        'beer': {'icon': 'mdi:beer', 'color': '#FFD700'},
        'bjór': {'icon': 'mdi:beer', 'color': '#FFD700'},
        'wine': {'icon': 'mdi:glass-wine', 'color': '#8B0000'},
        'vín': {'icon': 'mdi:glass-wine', 'color': '#8B0000'},
        'coffee': {'icon': 'mdi:coffee', 'color': '#8B4513'},
        'kaffi': {'icon': 'mdi:coffee', 'color': '#8B4513'},
        'tea': {'icon': 'mdi:tea', 'color': '#228B22'},
        'te': {'icon': 'mdi:tea', 'color': '#228B22'},
        
        # Sauces
        'sauce': {'icon': 'game-icons:ketchup', 'color': '#FF4500'},
        'sósa': {'icon': 'game-icons:ketchup', 'color': '#FF4500'},
        'ketchup': {'icon': 'game-icons:ketchup', 'color': '#FF0000'},
        'mayo': {'icon': 'game-icons:ketchup', 'color': '#FFFFF0'},
        'mustard': {'icon': 'game-icons:ketchup', 'color': '#FFD700'},
        'sinnep': {'icon': 'game-icons:ketchup', 'color': '#FFD700'},
        
        # Desserts
        'ice-cream': {'icon': 'mdi:ice-cream', 'color': '#FF69B4'},
        'ís': {'icon': 'mdi:ice-cream', 'color': '#FF69B4'},
        'cake': {'icon': 'mdi:cake-variant', 'color': '#FF69B4'},
        'kaka': {'icon': 'mdi:cake-variant', 'color': '#FF69B4'},
        'cookie': {'icon': 'mdi:cookie', 'color': '#D2691E'},
        'kex': {'icon': 'mdi:cookie', 'color': '#D2691E'},
        'dessert': {'icon': 'mdi:ice-cream', 'color': '#FF69B4'},
        'eftirréttur': {'icon': 'mdi:ice-cream', 'color': '#FF69B4'},
        
        # Fish
        'fish': {'icon': 'mdi:fish', 'color': '#4A90E2'},
        'fiskur': {'icon': 'mdi:fish', 'color': '#4A90E2'},
        'salmon': {'icon': 'mdi:fish', 'color': '#FF6B6B'},
        'lax': {'icon': 'mdi:fish', 'color': '#FF6B6B'},
        'cod': {'icon': 'mdi:fish', 'color': '#4A90E2'},
        'þorskur': {'icon': 'mdi:fish', 'color': '#4A90E2'},
        'shrimp': {'icon': 'noto-v1:shrimp', 'color': '#FF6B6B'},
        'rækja': {'icon': 'noto-v1:shrimp', 'color': '#FF6B6B'},
        
        # Generic
        'main': {'icon': 'mdi:food', 'color': '#8B4513'},
        'side': {'icon': 'mdi:food-fork-drink', 'color': '#228B22'},
        'drink': {'icon': 'mdi:cup', 'color': '#4A90E2'},
        'snack': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'fruit': {'icon': 'mdi:food-apple', 'color': '#228B22'},
        'ávöxtur': {'icon': 'mdi:food-apple', 'color': '#228B22'},
        'soup': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'suppa': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'curry': {'icon': 'mdi:food-variant', 'color': '#FF6B35'},
        'kebab': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'quesadilla': {'icon': 'mdi:food-variant', 'color': '#FFD700'},
        'burrito': {'icon': 'mdi:food-variant', 'color': '#228B22'},
        'enchilada': {'icon': 'mdi:food-variant', 'color': '#FF6B35'},
        'fajita': {'icon': 'mdi:food-variant', 'color': '#FFD700'},
        'gyro': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'shawarma': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'falafel': {'icon': 'mdi:food-variant', 'color': '#228B22'},
        'dumpling': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'springroll': {'icon': 'mdi:food-variant', 'color': '#228B22'},
        'eggroll': {'icon': 'mdi:food-variant', 'color': '#FFD700'},
        'tempura': {'icon': 'mdi:food-variant', 'color': '#FFD700'},
        'teriyaki': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'stirfry': {'icon': 'mdi:food-variant', 'color': '#228B22'},
        'lo mein': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'pad thai': {'icon': 'mdi:food-variant', 'color': '#FFD700'},
        'pho': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'ramen': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'udon': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'soba': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'bibimbap': {'icon': 'mdi:food-variant', 'color': '#FF6B35'},
        'bulgogi': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'japchae': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'kimchi': {'icon': 'mdi:food-variant', 'color': '#FF6B35'},
        'taco': {'icon': 'mdi:food-variant', 'color': '#FFD700'},
        'thai': {'icon': 'mdi:food-variant', 'color': '#FF6B35'},
        'noodlesoup': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'noodles': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'núðlur': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'pasta': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'sushi': {'icon': 'mdi:food-variant', 'color': '#FF6B6B'},
    }
    
    # Tag Icons (for offer tags)
    TAG_ICONS = {
        'Borgari': {'icon': 'fluent-emoji:hamburger', 'color': '#8B4513'},
        'Kjúklingur': {'icon': 'mdi:food-drumstick', 'color': '#D4AF37'},
        'Nautakjöt': {'icon': 'mdi:food-steak', 'color': '#8B4513'},
        'Pizza': {'icon': 'twemoji:pizza', 'color': '#FF6B35'},
        'Franskar': {'icon': 'mdi:food-french-fries', 'color': '#8B4513'},
        'Sub': {'icon': 'mdi:food-sandwich', 'color': '#228B22'},
        'Gos': {'icon': 'mdi:cup', 'color': '#000000'},
        'Drykkur': {'icon': 'mdi:cup', 'color': '#4A90E2'},
        'Fiskur': {'icon': 'mdi:fish', 'color': '#4A90E2'},
        'Rækjur': {'icon': 'noto-v1:shrimp', 'color': '#FF6B6B'},
        'Pasta': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'Sushi': {'icon': 'mdi:food-variant', 'color': '#FF6B6B'},
        'Thai': {'icon': 'mdi:food-variant', 'color': '#FF6B35'},
        'Núðlur': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'Núðlusúp': {'icon': 'mdi:food-variant', 'color': '#8B4513'},
        'Vegan': {'icon': 'mdi:food-variant', 'color': '#228B22'},
    }
    
    @classmethod
    def _load_food_icons(cls):
        """Load icon mappings from JSON and cache them"""
        if not hasattr(cls, '_icons_cache'):
            json_path = Path(__file__).resolve().parent.parent / 'food_icon_mapping.json'
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    cls._icons_cache = json.load(f)
            except FileNotFoundError:
                cls._icons_cache = {}
        return cls._icons_cache
    
    @classmethod
    def get_food_icon(cls, food_type: str, category: str = None) -> Dict[str, str]:
        """Get icon and color for a food item using JSON mapping"""
        icons = cls._load_food_icons()
        normalized_type = food_type.lower().strip()
        normalized_category = category.lower().strip() if category else None

        # Try exact match first
        if normalized_type in icons:
            return icons[normalized_type]

        # Try category match
        if normalized_category and normalized_category in icons:
            return icons[normalized_category]

        # Try partial matches
        for key, mapping in icons.items():
            if normalized_type in key or key in normalized_type:
                return mapping

        # Default fallback
        return {'icon': 'mdi:food', 'color': '#8B4513'}
    
    @classmethod
    def generate_standardized_tags(cls, offer: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate standardized tags for an offer"""
        tags = []
        all_items = offer.get('food_items', [])
        
        # Chicken
        if any(item.get('type') == 'chicken' or 'kjúkling' in item.get('name', '').lower() 
               for item in all_items):
            tag_icon = cls.TAG_ICONS['Kjúklingur']
            tags.append({
                'label': 'Kjúklingur',
                'icon': tag_icon['icon'],
                'color': tag_icon['color']
            })
        
        # Beef
        if any(item.get('type') == 'beef' or 'nautakjöt' in item.get('name', '').lower() 
               for item in all_items):
            tag_icon = cls.TAG_ICONS['Nautakjöt']
            tags.append({
                'label': 'Nautakjöt',
                'icon': tag_icon['icon'],
                'color': tag_icon['color']
            })
        
        # Pizza
        if any(item.get('type') == 'pizza' or 'pizza' in item.get('name', '').lower() 
               for item in all_items):
            tag_icon = cls.TAG_ICONS['Pizza']
            tags.append({
                'label': 'Pizza',
                'icon': tag_icon['icon'],
                'color': tag_icon['color']
            })
        
        # French fries
        if any('franskar' in item.get('name', '').lower() or 'pommes' in item.get('name', '').lower() 
               for item in all_items):
            tag_icon = cls.TAG_ICONS['Franskar']
            tags.append({
                'label': 'Franskar',
                'icon': tag_icon['icon'],
                'color': tag_icon['color']
            })
        
        # Sub/Bátur
        if any('bátur' in item.get('name', '').lower() or 'sub' in item.get('name', '').lower() 
               for item in all_items):
            tag_icon = cls.TAG_ICONS['Sub']
            tags.append({
                'label': 'Sub',
                'icon': tag_icon['icon'],
                'color': tag_icon['color']
            })
        
        # Drink included - check if it's soda/gos
        drink_items = offer.get('drink_items', [])
        if drink_items:
            has_soda = any(
                'gos' in drink.get('name', '').lower() or 
                'soda' in drink.get('name', '').lower() or 
                'kók' in drink.get('name', '').lower() or
                'pepsi' in drink.get('name', '').lower()
                for drink in drink_items
            )
            if has_soda:
                tag_icon = cls.TAG_ICONS['Gos']
                tags.append({
                    'label': 'Gos',
                    'icon': tag_icon['icon'],
                    'color': tag_icon['color']
                })
            else:
                tag_icon = cls.TAG_ICONS['Drykkur']
                tags.append({
                    'label': 'Drykkur',
                    'icon': tag_icon['icon'],
                    'color': tag_icon['color']
                })
        
        return tags[:3]  # Limit to 3 tags
    
    @classmethod
    def enhance_food_item(cls, food_item: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a food item with proper icon and color"""
        food_type = food_item.get('type', '')
        category = food_item.get('category', '')
        name = food_item.get('name', '')
        
        # Get icon mapping
        icon_mapping = cls.get_food_icon(food_type, category)
        
        # Update the food item
        enhanced_item = food_item.copy()
        enhanced_item['icon'] = icon_mapping['icon']
        enhanced_item['icon_color'] = icon_mapping['color']
        
        return enhanced_item
    
    @classmethod
    def enhance_offer(cls, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance an offer with all necessary display information"""
        enhanced_offer = offer.copy()
        
        # Enhance all food items
        if 'food_items' in enhanced_offer:
            enhanced_offer['food_items'] = [
                cls.enhance_food_item(item) for item in enhanced_offer['food_items']
            ]
        
        if 'main_items' in enhanced_offer:
            enhanced_offer['main_items'] = [
                cls.enhance_food_item(item) for item in enhanced_offer['main_items']
            ]
        
        if 'side_items' in enhanced_offer:
            enhanced_offer['side_items'] = [
                cls.enhance_food_item(item) for item in enhanced_offer['side_items']
            ]
        
        if 'drink_items' in enhanced_offer:
            enhanced_offer['drink_items'] = [
                cls.enhance_food_item(item) for item in enhanced_offer['drink_items']
            ]
        
        if 'dessert_items' in enhanced_offer:
            enhanced_offer['dessert_items'] = [
                cls.enhance_food_item(item) for item in enhanced_offer['dessert_items']
            ]
        
        # Generate standardized tags
        enhanced_offer['standardized_tags'] = cls.generate_standardized_tags(enhanced_offer)
        
        # Add display properties
        enhanced_offer['display_properties'] = {
            'show_category_headers': False,  # Don't show aðalréttur, meðlæmi, etc.
            'show_fallback_info': False,    # Don't show "Upplýsingar" section
            'compact_view': True,           # Use compact food visualization
            'max_tags': 3                   # Maximum number of tags to show
        }
        
        return enhanced_offer 