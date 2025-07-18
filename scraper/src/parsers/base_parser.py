import requests
import logging
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod
from llm_food_extractor import LLMFoodExtractor  # Changed from food_extractor

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Base parser class with common functionality for all restaurant parsers"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Initialize LLM food extractor instead of the old one
        self.food_extractor = LLMFoodExtractor()
        
        # Icelandic weekday patterns with proper declensions (4 cases: nominative, accusative, dative, genitive)
        # Including both singular and plural forms with word boundaries to avoid false matches
        self.weekday_patterns = {
            'monday': [
                # Singular forms
                r'\bmánudagur\b',      # nominative
                r'\bmánudag\b',        # accusative  
                r'\bmánudegi\b',       # dative
                r'\bmánudags\b',       # genitive
                r'\bmánudaginn\b',     # definite forms
                r'\bmánudeginum\b',
                r'\bmánudagsins\b',
                # Plural forms
                r'\bmánudagar\b',      # nominative plural
                r'\bmánudaga\b',       # accusative plural
                r'\bmánudögum\b',      # dative plural
                r'\bmánudaga\b',       # genitive plural (same as accusative)
            ],
            'tuesday': [
                # Singular forms
                r'\bþriðjudagur\b',
                r'\bþriðjudag\b', 
                r'\bþriðjudegi\b',
                r'\bþriðjudags\b',
                r'\bþriðjudaginn\b',
                r'\bþriðjudeginum\b',
                r'\bþriðjudagsins\b',
                # Plural forms
                r'\bþriðjudagar\b',    # nominative plural
                r'\bþriðjudaga\b',     # accusative plural
                r'\bþriðjudögum\b',    # dative plural
                r'\bþriðjudaga\b',     # genitive plural (same as accusative)
            ],
            'wednesday': [
                # Singular forms
                r'\bmiðvikudagur\b',
                r'\bmiðvikudag\b',
                r'\bmiðvikudegi\b', 
                r'\bmiðvikudags\b',
                r'\bmiðvikudaginn\b',
                r'\bmiðvikudeginum\b',
                r'\bmiðvikudagsins\b',
                # Plural forms
                r'\bmiðvikudagar\b',   # nominative plural
                r'\bmiðvikudaga\b',    # accusative plural
                r'\bmiðvikudögum\b',   # dative plural
                r'\bmiðvikudaga\b',    # genitive plural (same as accusative)
            ],
            'thursday': [
                # Singular forms
                r'\bfimmtudagur\b',
                r'\bfimmtudag\b',
                r'\bfimmtudegi\b',
                r'\bfimmtudags\b', 
                r'\bfimmtudaginn\b',
                r'\bfimmtudeginum\b',
                r'\bfimmtudagsins\b',
                # Plural forms
                r'\bfimmtudagar\b',    # nominative plural
                r'\bfimmtudaga\b',     # accusative plural
                r'\bfimmtudögum\b',    # dative plural
                r'\bfimmtudaga\b',     # genitive plural (same as accusative)
            ],
            'friday': [
                # Singular forms
                r'\bföstudagur\b',
                r'\bföstudag\b',
                r'\bföstudegi\b',
                r'\bföstudags\b',
                r'\bföstudaginn\b', 
                r'\bföstudeginum\b',
                r'\bföstudagsins\b',
                # Plural forms
                r'\bföstudagar\b',     # nominative plural
                r'\bföstudaga\b',      # accusative plural
                r'\bföstudögum\b',     # dative plural
                r'\bföstudaga\b',      # genitive plural (same as accusative)
            ],
            'saturday': [
                # Singular forms
                r'\blaugardagur\b',
                r'\blaugardag\b',
                r'\blaugardegi\b',
                r'\blaugardags\b',
                r'\blaugardaginn\b',
                r'\blaugardeginum\b',
                r'\blaugardagsins\b',
                # Plural forms
                r'\blaugardagar\b',    # nominative plural
                r'\blaugardaga\b',     # accusative plural
                r'\blaugardögum\b',    # dative plural
                r'\blaugardaga\b',     # genitive plural (same as accusative)
            ],
            'sunday': [
                # Singular forms
                r'\bsunnudagur\b',
                r'\bsunnudag\b',
                r'\bsunnudegi\b', 
                r'\bsunnudags\b',
                r'\bsunnudaginn\b',
                r'\bsunnudeginum\b',
                r'\bsunnudagsins\b',
                # Plural forms
                r'\bsunnudagar\b',     # nominative plural
                r'\bsunnudaga\b',      # accusative plural
                r'\bsunnudögum\b',     # dative plural
                r'\bsunnudaga\b',      # genitive plural (same as accusative)
            ]
        }
        
        # Special day groups
        self.special_day_patterns = {
            'weekdays': [
                r'\bvirka daga\b',
                r'\bvirkir dagar\b', 
                r'\bvirkum dögum\b',
                r'\bvikudaga\b',
                r'\bvegna vikudaga\b',
            ],
            'weekend': [
                r'\bhelgar\b',
                r'\bhelgi\b',
                r'\bum helgar\b',
                r'\bá helgum\b',
            ]
        }
        
        # Field extraction statistics
        self.field_stats = {
            'offers_found': 0,
            'name_extracted': 0,
            'description_extracted': 0,
            'price_extracted': 0,
            'pickup_delivery_extracted': 0,
            'suits_people_extracted': 0,
            'weekdays_extracted': 0,
            'hours_extracted': 0,
            'food_extracted': 0
        }
    
    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page"""
        try:
            logger.info(f"Fetching page: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            logger.info(f"Successfully parsed page with {len(soup.find_all())} elements")
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse {url}: {e}")
            raise
    
    def extract_price_kr(self, text: str) -> Optional[float]:
        """Extract price in Icelandic krónur from text"""
        if not text:
            return None
            
        # Look for patterns like "1.290 kr.", "1290kr", "1,290 kr", etc.
        price_patterns = [
            r'(\d{1,3}(?:[.,]\d{3})*)\s*kr\.?',  # 1.290 kr, 1,290 kr
            r'(\d+)\s*kr\.?',  # Simple 1290 kr
            r'kr\.?\s*(\d{1,3}(?:[.,]\d{3})*)',  # kr. 1290
            r'(\d{1,3}(?:[.,]\d{3})*)\s*krónur?',  # 1290 krónur
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace('.', '').replace(',', '')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_pickup_delivery(self, text: str) -> Optional[str]:
        """Extract pickup/delivery information (sækja/sótt)"""
        if not text:
            return None
            
        text_lower = text.lower()
        
        # Look for Icelandic terms
        pickup_terms = ['sækja', 'sótt', 'afhending', 'pickup', 'collection']
        delivery_terms = ['sending', 'heimsending', 'delivery', 'delivered']
        
        found_terms = []
        
        for term in pickup_terms:
            if term in text_lower:
                found_terms.append('sækja')
                break
        
        for term in delivery_terms:
            if term in text_lower:
                found_terms.append('sending')
                break
        
        if found_terms:
            return '/'.join(found_terms)
        
        return None
    
    def extract_suits_people(self, text: str) -> Optional[int]:
        """Extract number of people the offer suits"""
        if not text:
            return None
            
        # Look for patterns like "2 people", "fyrir 4", "4 manna", etc.
        people_patterns = [
            r'(\d+)\s*(?:people|person|manna|manns)',
            r'fyrir\s*(\d+)',
            r'(\d+)\s*(?:manna|manns)',
            r'(\d+)(?:-|\s)?(?:person|people)',
        ]
        
        for pattern in people_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        text = text.strip()
        
        return text
    
    def extract_weekdays(self, text: str) -> Optional[str]:
        """Extract Icelandic weekdays from text using precise regex patterns"""
        if not text:
            return None
            
        text_lower = text.lower()
        found_weekdays = []
        
        # Map English day names to Icelandic normalized forms
        day_name_mapping = {
            'monday': 'mánudagur',
            'tuesday': 'þriðjudagur', 
            'wednesday': 'miðvikudagur',
            'thursday': 'fimmtudagur',
            'friday': 'föstudagur',
            'saturday': 'laugardagur',
            'sunday': 'sunnudagur'
        }
        
        # Check for each weekday using regex patterns with word boundaries
        for english_day, patterns in self.weekday_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    icelandic_day = day_name_mapping[english_day]
                    if icelandic_day not in found_weekdays:
                        found_weekdays.append(icelandic_day)
                    break  # Found a match for this day, no need to check other patterns
        
        # Handle special day groups
        for group_name, patterns in self.special_day_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if group_name == 'weekdays':
                        # Add all weekdays
                        weekday_list = ['mánudagur', 'þriðjudagur', 'miðvikudagur', 'fimmtudagur', 'föstudagur']
                        for day in weekday_list:
                            if day not in found_weekdays:
                                found_weekdays.append(day)
                    elif group_name == 'weekend':
                        # Add weekend days
                        weekend_list = ['laugardagur', 'sunnudagur']
                        for day in weekend_list:
                            if day not in found_weekdays:
                                found_weekdays.append(day)
                    break  # Found a match for this group, no need to check other patterns
        
        return ','.join(found_weekdays) if found_weekdays else None
    
    def extract_hours(self, text: str) -> Optional[str]:
        """Extract time ranges from text"""
        if not text:
            return None
            
        # Time patterns to look for - ONLY complete time formats
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})',  # 11:00-15:00
            r'(\d{1,2})\.(\d{2})\s*-\s*(\d{1,2})\.(\d{2})',  # 11.00-15.00  
            r'frá\s+(\d{1,2}):(\d{2})\s+til\s+(\d{1,2}):(\d{2})',  # frá 11:00 til 15:00
            r'milli\s+(\d{1,2}):(\d{2})\s+og\s+(\d{1,2}):(\d{2})',  # milli 11:00 og 15:00
            r'kl\.?\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})',  # kl. 11:00-15:00
        ]
        
        found_times = []
        
        for pattern in time_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) == 4:
                    # Full time format (HH:MM-HH:MM)
                    start_hour, start_min, end_hour, end_min = groups
                    time_range = f"{start_hour.zfill(2)}:{start_min.zfill(2)}-{end_hour.zfill(2)}:{end_min.zfill(2)}"
                    
                    if time_range not in found_times:
                        found_times.append(time_range)
        
        # Look for specific meal times in Icelandic
        meal_times = {
            'hádegi': '11:00-15:00',
            'hádegis': '11:00-15:00',
            'morgun': '07:00-11:00',
            'kvöld': '17:00-22:00',
            'nótt': '22:00-06:00',
        }
        
        text_lower = text.lower()
        for meal, time_range in meal_times.items():
            if meal in text_lower and time_range not in found_times:
                found_times.append(time_range)
        
        return ','.join(found_times) if found_times else None
    
    def extract_temporal_info(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract both weekdays and hours from text, return (weekdays, hours, availability_text)"""
        if not text:
            return None, None, None
        
        # Extract weekdays and hours
        weekdays = self.extract_weekdays(text)
        hours = self.extract_hours(text)
        
        # Determine if this text contains temporal information
        temporal_indicators = [
            'dag', 'vikudaga', 'virka', 'helgi', 'helgar',
            'mánudagur', 'þriðjudagur', 'miðvikudagur', 'fimmtudagur', 'föstudagur', 'laugardagur', 'sunnudagur',
            'hádegi', 'morgun', 'kvöld', 'klukkan', 'frá', 'til', 'milli',
            ':', '-', 'kl'
        ]
        
        text_lower = text.lower()
        has_temporal_info = any(indicator in text_lower for indicator in temporal_indicators)
        
        # Only save availability_text if it actually contains temporal information
        availability_text = text if has_temporal_info and (weekdays or hours) else None
        
        return weekdays, hours, availability_text
    
    def log_field_stats(self, restaurant_name: str):
        """Log field extraction statistics"""
        logger.info(f"=== {restaurant_name} FIELD EXTRACTION STATS ===")
        logger.info(f"Offers found: {self.field_stats['offers_found']}")
        logger.info(f"Names extracted: {self.field_stats['name_extracted']}/{self.field_stats['offers_found']}")
        logger.info(f"Descriptions extracted: {self.field_stats['description_extracted']}/{self.field_stats['offers_found']}")
        logger.info(f"Prices extracted: {self.field_stats['price_extracted']}/{self.field_stats['offers_found']}")
        logger.info(f"Pickup/delivery extracted: {self.field_stats['pickup_delivery_extracted']}/{self.field_stats['offers_found']}")
        logger.info(f"Suits people extracted: {self.field_stats['suits_people_extracted']}/{self.field_stats['offers_found']}")
        logger.info(f"Weekdays extracted: {self.field_stats['weekdays_extracted']}/{self.field_stats['offers_found']}")
        logger.info(f"Hours extracted: {self.field_stats['hours_extracted']}/{self.field_stats['offers_found']}")
        logger.info(f"Food extracted: {self.field_stats['food_extracted']}/{self.field_stats['offers_found']}")
    
    def enhance_offers_with_food_info(self, offers: List[Dict]) -> List[Dict]:
        """Enhance offers with detailed food information for visual representations"""
        if not offers:
            return []
        
        # Use LLM extractor's batch processing for better results
        try:
            food_info_list = self.food_extractor.extract_food_info_batch(offers)
            
            # Merge food information with original offer data
            enhanced_offers = []
            for i, offer in enumerate(offers):
                enhanced_offer = offer.copy()  # Start with original offer data
                
                # Add food information from LLM extractor
                if i < len(food_info_list):
                    food_info = food_info_list[i]
                    enhanced_offer.update(food_info)
                    
                    # Update statistics for extracted food items
                    if food_info.get('food_items'):
                        self.field_stats['food_extracted'] += 1
                else:
                    # Fallback: add empty food info
                    enhanced_offer.update(self._get_empty_food_info())
                
                enhanced_offers.append(enhanced_offer)
            
            return enhanced_offers
            
        except Exception as e:
            logger.error(f"Failed to extract food info using LLM extractor: {e}")
            
            # Fallback: add empty food info to all offers
            enhanced_offers = []
            for offer in offers:
                enhanced_offer = offer.copy()
                enhanced_offer.update(self._get_empty_food_info())
                enhanced_offers.append(enhanced_offer)
            
            return enhanced_offers
    
    def _get_empty_food_info(self) -> Dict:
        """Get empty food info structure for fallback cases"""
        return {
            'food_items': [],
            'meal_type': 'snack',
            'is_combo': False,
            'complexity_score': 0,
            'total_food_items': 0,
            'main_items': [],
            'side_items': [],
            'drink_items': [],
            'dessert_items': [],
            'visual_summary': '🍽️ General offer'
        }

    def prepare_offers_for_database(self, enhanced_offers: List[Dict]) -> List[Dict]:
        """Prepare enhanced offers for database saving by filtering out food information fields"""
        # Database-compatible fields (from the Offer model)
        db_fields = {
            'offer_name', 'description', 'price_kr', 'pickup_delivery', 'suits_people',
            'available_weekdays', 'available_hours', 'availability_text', 
            'source_url', 'restaurant_id'
        }
        
        db_offers = []
        for offer in enhanced_offers:
            # Create a clean copy with only database-compatible fields
            db_offer = {key: value for key, value in offer.items() if key in db_fields}
            db_offers.append(db_offer)
        
        return db_offers

    @abstractmethod
    def scrape_offers(self, url: str) -> List[Dict]:
        """Scrape offers from the given URL - must be implemented by subclasses"""
        pass 