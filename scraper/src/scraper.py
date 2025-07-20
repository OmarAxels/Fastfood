import logging
import time
import json
from pathlib import Path
from typing import Dict, List
from json_reader import FastfoodInfoReader
from parsers.kfc_parser import KFCParser
from parsers.subway_parser import SubwayParser
from parsers.ai_parser import AIParser
from parsers.bullan_parser import BullanParser
from parsers.dominos_parser import DominosParser
from config import PARSER_CONFIG, CRAWL_DELAY
from datetime import datetime, timezone
from icon_mapping import IconMapping

logger = logging.getLogger(__name__)


class FastfoodScraper:
    """Main scraper class that coordinates scraping from multiple fastfood websites"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.json_reader = FastfoodInfoReader()
        
        # Initialize parsers based on configuration
        self.parsers = {}
        self._initialize_parsers()
        
        # Statistics tracking
        self.stats = {
            'total_offers': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'restaurants_processed': 0,
            'offers_saved': 0
        }
        
        # Storage for enhanced offers with food information
        self.enhanced_offers_data = []
    
    def _initialize_parsers(self):
        """Initialize parsers based on configuration"""
        for restaurant_name, parser_type in PARSER_CONFIG.items():
            if parser_type == 'ai':
                self.parsers[restaurant_name] = AIParser()
            elif parser_type == 'bullan':
                self.parsers[restaurant_name] = BullanParser()
            elif parser_type == 'traditional':
                # Map restaurant names to their traditional parsers
                if restaurant_name == 'KFC Iceland':
                    self.parsers[restaurant_name] = KFCParser()
                elif restaurant_name == "Domino's Pizza Iceland":
                    self.parsers[restaurant_name] = DominosParser()
                elif restaurant_name == 'Subway Iceland':
                    self.parsers[restaurant_name] = SubwayParser()
                else:
                    logger.warning(f"No traditional parser available for {restaurant_name}")
            else:
                logger.warning(f"Unknown parser type '{parser_type}' for {restaurant_name}")
    
    def _get_parser_for_restaurant(self, restaurant_name: str):
        """Get the appropriate parser for a restaurant, defaulting to AI parser"""
        # Check if we have a specific parser configured
        if restaurant_name in self.parsers:
            return self.parsers[restaurant_name]
        
        # Default to AI parser for new restaurants
        logger.info(f"No specific parser configured for {restaurant_name}, using AI parser")
        return AIParser()
    
    def run(self):
        """Run the complete scraping process"""
        logger.info("Starting fastfood scraper")
        
        try:
            restaurants = self.json_reader.load_restaurants()
            
            for restaurant in restaurants:
                self.stats['restaurants_processed'] += 1
                self._scrape_restaurant(restaurant)
                
                # Small delay between restaurants to be respectful
                time.sleep(CRAWL_DELAY)
            
            self._log_summary()
            
            # Save enhanced offers with food information to JSON file
            self._save_enhanced_offers_json()
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise
    
    def _scrape_restaurant(self, restaurant: Dict):
        """Scrape offers from a single restaurant"""
        restaurant_name = restaurant['name']
        offers_url = restaurant['offers_page']
        
        logger.info(f"Scraping {restaurant_name} from {offers_url}")
        
        try:
            # Get appropriate parser
            parser = self._get_parser_for_restaurant(restaurant_name)
            
            # Scrape offers
            offers = parser.scrape_offers(offers_url)
            
            if not offers:
                logger.warning(f"No offers found for {restaurant_name}")
                self.stats['failed_scrapes'] += 1
                return
            
            # Enhance offers with food information for visual representations
            enhanced_offers = parser.enhance_offers_with_food_info(offers)
            
            # Further enhance offers with icon mapping and display properties
            for offer in enhanced_offers:
                offer['restaurant_name'] = restaurant_name
                # Apply icon mapping and display enhancements
                enhanced_offer = IconMapping.enhance_offer(offer)
                self.enhanced_offers_data.append(enhanced_offer)
            
            # Prepare database-compatible offers (without food information fields)
            db_offers = parser.prepare_offers_for_database(enhanced_offers)
            
            # Add source_url to each offer
            for offer in db_offers:
                offer['source_url'] = offers_url
            
            # Use batch save method to clear existing offers and save new ones
            try:
                saved_count = self.db_manager.save_offers_batch(
                    offers_data=db_offers,
                    restaurant_data=restaurant,
                    clear_existing=True  # This will overwrite old data
                )
                self.stats['offers_saved'] += saved_count
                self.stats['total_offers'] += len(enhanced_offers)
                self.stats['successful_scrapes'] += 1
                logger.info(f"Successfully scraped {len(enhanced_offers)} offers from {restaurant_name}")
            except Exception as e:
                logger.error(f"Failed to save offers for {restaurant_name}: {e}")
                # Fallback to individual saves (backward compatibility)
                saved_count = 0
                for offer in db_offers:
                    try:
                        self.db_manager.save_offer(offer, restaurant)
                        saved_count += 1
                    except Exception as save_error:
                        logger.error(f"Failed to save individual offer: {save_error}")
                
                if saved_count > 0:
                    self.stats['offers_saved'] += saved_count
                    self.stats['total_offers'] += len(enhanced_offers)
                    self.stats['successful_scrapes'] += 1
                    logger.info(f"Successfully saved {saved_count}/{len(enhanced_offers)} offers from {restaurant_name}")
                else:
                    self.stats['failed_scrapes'] += 1
            
        except Exception as e:
            logger.error(f"Failed to scrape {restaurant_name}: {e}")
            self.stats['failed_scrapes'] += 1
    
    def _log_summary(self):
        """Log a summary of the scraping session"""
        logger.info("=== SCRAPING SUMMARY ===")
        logger.info(f"Restaurants processed: {self.stats['restaurants_processed']}")
        logger.info(f"Successful scrapes: {self.stats['successful_scrapes']}")
        logger.info(f"Failed scrapes: {self.stats['failed_scrapes']}")
        logger.info(f"Total offers found: {self.stats['total_offers']}")
        logger.info(f"Offers saved to database: {self.stats['offers_saved']}")
        
        success_rate = (self.stats['successful_scrapes'] / self.stats['restaurants_processed']) * 100 if self.stats['restaurants_processed'] > 0 else 0
        logger.info(f"Success rate: {success_rate:.1f}%")
        
        # Log detailed field extraction success
        self._log_field_extraction_summary()
    
    def _log_field_extraction_summary(self):
        """Log detailed summary of which fields were successfully extracted"""
        logger.info("=== FIELD EXTRACTION SUMMARY ===")
        
        # This would be populated by parsers during scraping
        # For now, we'll add this functionality to the parsers
        logger.info("Field extraction details will be logged by individual parsers")
    
    def _save_enhanced_offers_json(self):
        """Save enhanced offers with food information to a JSON file"""
        if not self.enhanced_offers_data:
            logger.info("No enhanced offers data to save")
            return
        
        try:
            # Create enhanced offers file path
            output_file = Path("enhanced_offers_with_food_info.json")
            backend_output_file = Path("../backend/enhanced_offers_with_food_info.json")
            
            # Ensure backend directory exists
            backend_output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for JSON serialization
            json_data = {
                'scraped_at': datetime.now(timezone.utc).isoformat(),
                'total_offers': len(self.enhanced_offers_data),
                'restaurants': list(set(offer['restaurant_name'] for offer in self.enhanced_offers_data)),
                'offers': []
            }
            
            # Convert offers to JSON-serializable format
            for offer in self.enhanced_offers_data:
                json_offer = {}
                for key, value in offer.items():
                    # Handle datetime objects
                    if hasattr(value, 'isoformat'):
                        json_offer[key] = value.isoformat()
                    else:
                        json_offer[key] = value
                json_data['offers'].append(json_offer)
            
            # Save to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            with open(backend_output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.enhanced_offers_data)} enhanced offers with food information to {output_file}")
            logger.info(f"Saved {len(self.enhanced_offers_data)} enhanced offers with food information to {backend_output_file}")
        except Exception as e:
            logger.error(f"Failed to save enhanced offers JSON: {e}") 