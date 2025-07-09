import logging
import time
from typing import Dict, List
from json_reader import FastfoodInfoReader
from parsers.kfc_parser import KFCParser
from parsers.dominos_parser import DominosParser

logger = logging.getLogger(__name__)


class FastfoodScraper:
    """Main scraper class that coordinates scraping from multiple fastfood websites"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.json_reader = FastfoodInfoReader()
        
        # Initialize parsers
        self.parsers = {
            'KFC Iceland': KFCParser(),
            "Domino's Pizza Iceland": DominosParser()
        }
        
        # Statistics tracking
        self.stats = {
            'total_offers': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'restaurants_processed': 0,
            'offers_saved': 0
        }
    
    def run(self):
        """Run the complete scraping process"""
        logger.info("Starting fastfood scraper")
        
        try:
            restaurants = self.json_reader.load_restaurants()
            
            for restaurant in restaurants:
                self.stats['restaurants_processed'] += 1
                self._scrape_restaurant(restaurant)
                
                # Small delay between restaurants to be respectful
                time.sleep(2)
            
            self._log_summary()
            
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
            parser = self.parsers.get(restaurant_name)
            if not parser:
                logger.warning(f"No parser available for {restaurant_name}")
                self.stats['failed_scrapes'] += 1
                return
            
            # Scrape offers
            offers = parser.scrape_offers(offers_url)
            
            if not offers:
                logger.warning(f"No offers found for {restaurant_name}")
                self.stats['failed_scrapes'] += 1
                return
            
            # Add source_url to each offer
            for offer in offers:
                offer['source_url'] = offers_url
            
            # Use batch save method to clear existing offers and save new ones
            try:
                saved_count = self.db_manager.save_offers_batch(
                    offers_data=offers,
                    restaurant_data=restaurant,
                    clear_existing=True  # This will overwrite old data
                )
                self.stats['offers_saved'] += saved_count
                self.stats['total_offers'] += len(offers)
                self.stats['successful_scrapes'] += 1
                logger.info(f"Successfully scraped {len(offers)} offers from {restaurant_name}")
            except Exception as e:
                logger.error(f"Failed to save offers for {restaurant_name}: {e}")
                # Fallback to individual saves (backward compatibility)
                saved_count = 0
                for offer in offers:
                    try:
                        self.db_manager.save_offer(offer, restaurant)
                        saved_count += 1
                    except Exception as save_error:
                        logger.error(f"Failed to save individual offer: {save_error}")
                
                if saved_count > 0:
                    self.stats['offers_saved'] += saved_count
                    self.stats['total_offers'] += len(offers)
                    self.stats['successful_scrapes'] += 1
                    logger.info(f"Successfully saved {saved_count}/{len(offers)} offers from {restaurant_name}")
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