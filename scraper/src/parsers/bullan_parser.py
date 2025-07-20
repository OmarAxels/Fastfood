import logging
import asyncio
from typing import List, Dict
from .base_parser import BaseParser
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class BullanParser(BaseParser):
    """Custom parser specifically for Búllan (tommis.is) that targets the tilbod section"""
    
    def scrape_offers(self, url: str) -> List[Dict]:
        """Scrape offers using custom HTML parsing for Búllan"""
        try:
            # Get HTML content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the tilbod section
            tilbod_section = soup.find('div', {'id': 'tilbod'})
            if not tilbod_section:
                logger.warning("Could not find div#tilbod section on Búllan website")
                return []
            
            offers = []
            
            # Find all offer items within tilbod section
            offer_items = tilbod_section.find_all('div', class_='col-sm-4')
            logger.info(f"Found {len(offer_items)} offer items in tilbod section")
            
            for item in offer_items:
                try:
                    # Extract offer name from h3
                    name_elem = item.find('h3')
                    if not name_elem:
                        continue
                    offer_name = name_elem.get_text(strip=True)
                    
                    # Extract price from .price span
                    price_elem = item.find('div', class_='price')
                    if price_elem:
                        price_span = price_elem.find('span')
                        if price_span:
                            price_text = price_span.get_text(strip=True)
                            price_kr = self._extract_price_kr(price_text)
                        else:
                            price_kr = None
                    else:
                        price_kr = None
                    
                    # Extract description from .offers-block p
                    desc_elem = item.find('div', class_='offers-block')
                    if desc_elem:
                        desc_p = desc_elem.find('p')
                        description = desc_p.get_text(strip=True) if desc_p else ""
                    else:
                        description = ""
                    
                    if offer_name:
                        offer = {
                            'offer_name': offer_name,
                            'description': description,
                            'price_kr': price_kr,
                            'pickup_delivery': None,
                            'suits_people': None,
                            'available_weekdays': None,
                            'available_hours': None,
                            'availability_text': None
                        }
                        offers.append(offer)
                        
                        # Update stats
                        self.field_stats['name_extracted'] += 1
                        if description:
                            self.field_stats['description_extracted'] += 1
                        if price_kr:
                            self.field_stats['price_extracted'] += 1
                        
                        logger.info(f"Extracted offer: {offer_name} - {price_kr} kr")
                        logger.info(f"  Description: {description}")
                
                except Exception as e:
                    logger.warning(f"Failed to parse offer item: {e}")
                    continue
            
            self.field_stats['offers_found'] = len(offers)
            self.log_field_stats("Búllan Custom Parser")
            
            return offers
            
        except Exception as e:
            logger.error(f"Failed to scrape offers from Búllan: {e}")
            return []
    
    def _extract_price_kr(self, price_text: str) -> int:
        """Extract price in krónur from text"""
        try:
            if not price_text:
                return None
            
            # Clean the input text
            price_text = str(price_text).strip()
            logger.debug(f"Extracting price from: '{price_text}'")
            
            # Try different patterns for price extraction
            patterns = [
                r'(\d{1,2}\.\d{3})\s*kr',  # "2.990 kr" or "3.190 kr"
                r'kr\s*(\d{1,2}\.\d{3})',  # "kr 2.990"
                r'(\d{1,2}\.\d{3})',       # Just "2.990"
                r'(\d{3,5})\s*kr',         # "2990 kr"
                r'kr\s*(\d{3,5})',         # "kr 2990"
                r'(\d{3,5})',              # Just "2990"
            ]
            
            for pattern in patterns:
                price_match = re.search(pattern, price_text, re.IGNORECASE)
                if price_match:
                    price_str = price_match.group(1)
                    
                    # Handle European decimal format (period as thousands separator)
                    if '.' in price_str and len(price_str.split('.')[-1]) == 3:
                        # European thousands separator (e.g., "2.990" = 2990)
                        price_str = price_str.replace('.', '')
                    
                    try:
                        price_int = int(price_str)
                        
                        # Validate price range (reasonable for Icelandic restaurant offers)
                        if 500 <= price_int <= 15000:
                            logger.debug(f"Successfully extracted price: {price_int} from '{price_text}'")
                            return price_int
                    except ValueError:
                        continue
            
            logger.warning(f"Could not extract price from: '{price_text}'")
            return None
                        
        except Exception as e:
            logger.debug(f"Failed to extract price from '{price_text}': {e}")
            return None