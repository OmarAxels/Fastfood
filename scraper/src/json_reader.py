import json
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


class FastfoodInfoReader:
    """Reads and parses fastfood restaurant information from JSON file"""
    
    def __init__(self, json_file_path: str = "fastfood-info.json"):
        self.json_file_path = Path(json_file_path)
        if not self.json_file_path.exists():
            raise FileNotFoundError(f"Fastfood info file not found: {json_file_path}")
    
    def load_restaurants(self) -> List[Dict]:
        """Load restaurant information from JSON file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                restaurants = json.load(f)
            
            logger.info(f"Loaded {len(restaurants)} restaurants from {self.json_file_path}")
            
            # Validate required fields
            for restaurant in restaurants:
                required_fields = ['name', 'website', 'offers_page']
                for field in required_fields:
                    if field not in restaurant:
                        raise ValueError(f"Missing required field '{field}' in restaurant: {restaurant}")
            
            return restaurants
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load restaurants: {e}")
            raise
    
    def get_restaurant_by_name(self, name: str) -> Dict:
        """Get a specific restaurant by name"""
        restaurants = self.load_restaurants()
        for restaurant in restaurants:
            if restaurant['name'].lower() == name.lower():
                return restaurant
        raise ValueError(f"Restaurant '{name}' not found") 