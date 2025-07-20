import requests
import logging
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from .base_parser import BaseParser
from llm_food_extractor import LLMFoodExtractor
import asyncio
import crawl4ai as c4a

logger = logging.getLogger(__name__)


class DominosParser(BaseParser):
    """Custom parser for Domino's Pizza Iceland with special handling for TRÍÓ offer"""
    
    def __init__(self):
        super().__init__()
        self.food_extractor = LLMFoodExtractor()
    
    def scrape_offers(self, url: str) -> List[Dict]:
        """Scrape offers from Domino's with special handling for TRÍÓ offer"""
        try:
            logger.info(f"Scraping Domino's offers from {url}")
            
            # Use AI parser to get all offers first
            from .ai_parser import AIParser
            ai_parser = AIParser()
            offers = ai_parser.scrape_offers(url)
            
            # Check for TRÍÓ offer and enhance it if found
            enhanced_offers = []
            for offer in offers:
                if self._is_trio_offer(offer):
                    logger.info(f"Found TRÍÓ offer: {offer['offer_name']}")
                    enhanced_offer = self._enhance_trio_offer(offer, url)
                    enhanced_offers.append(enhanced_offer)
                else:
                    enhanced_offers.append(offer)
            
            self.field_stats['offers_found'] = len(enhanced_offers)
            self.log_field_stats("Domino's Parser")
            
            return enhanced_offers
            
        except Exception as e:
            logger.error(f"Failed to scrape Domino's offers: {e}")
            return []
    
    def _extract_offers_from_page(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extract offers from the main page using traditional parsing"""
        offers = []
        
        try:
            # Try multiple approaches to find offers
            
            # Approach 1: Look for specific Domino's offer patterns
            offer_containers = soup.find_all(['div', 'article'], class_=re.compile(r'offer|tilbod|deal|product', re.I))
            
            # Approach 2: Look for elements with price information
            price_elements = soup.find_all(text=re.compile(r'\d+\s*kr', re.I))
            for price_elem in price_elements:
                parent = price_elem.parent
                if parent:
                    # Look for nearby title elements
                    title_elem = parent.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) or parent.find(class_=re.compile(r'title|name|heading', re.I))
                    if title_elem:
                        offer = self._extract_single_offer(parent)
                        if offer and offer.get('offer_name'):
                            offers.append(offer)
            
            # Approach 3: Look for any elements containing both price and text
            all_elements = soup.find_all(['div', 'section', 'article'])
            for elem in all_elements:
                text = elem.get_text()
                if re.search(r'\d+\s*kr', text, re.I) and len(text) > 20:
                    offer = self._extract_single_offer(elem)
                    if offer and offer.get('offer_name'):
                        offers.append(offer)
            
            # Remove duplicates based on offer name
            seen_names = set()
            unique_offers = []
            for offer in offers:
                if offer.get('offer_name') and offer['offer_name'] not in seen_names:
                    seen_names.add(offer['offer_name'])
                    unique_offers.append(offer)
            
            offers = unique_offers
            
            # If no offers found with traditional parsing, try AI parsing as fallback
            if not offers:
                logger.info("No offers found with traditional parsing, falling back to AI parsing")
                from .ai_parser import AIParser
                ai_parser = AIParser()
                offers = ai_parser.scrape_offers(url)
            
        except Exception as e:
            logger.error(f"Error extracting offers from page: {e}")
        
        return offers
    
    def _extract_single_offer(self, container) -> Optional[Dict]:
        """Extract a single offer from a container element"""
        try:
            # Get all text from the container
            all_text = container.get_text(strip=True)
            
            # Extract offer name - try multiple approaches
            offer_name = None
            
            # Approach 1: Look for heading elements
            name_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if name_elem:
                offer_name = name_elem.get_text(strip=True)
            
            # Approach 2: Look for elements with title-like classes
            if not offer_name:
                title_elem = container.find(class_=re.compile(r'title|name|heading', re.I))
                if title_elem:
                    offer_name = title_elem.get_text(strip=True)
            
            # Approach 3: Look for the first significant text (not price, not too short)
            if not offer_name:
                lines = all_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if (len(line) > 3 and len(line) < 100 and 
                        not re.search(r'\d+\s*kr', line, re.I) and
                        not line.isdigit()):
                        offer_name = line
                        break
            
            # Extract description
            description = None
            desc_elem = container.find(['p', 'span'], class_=re.compile(r'desc|text|content', re.I))
            if desc_elem:
                description = desc_elem.get_text(strip=True)
            
            # Extract price - try multiple approaches
            price_kr = None
            
            # Approach 1: Look for price elements
            price_elem = container.find(class_=re.compile(r'price|cost', re.I))
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_kr = self.extract_price_kr(price_text)
            
            # Approach 2: Look for price patterns in all text
            if not price_kr:
                price_match = re.search(r'(\d{1,3}(?:[.,]\d{3})*)\s*kr', all_text, re.I)
                if price_match:
                    price_kr = self.extract_price_kr(price_match.group(0))
            
            # Only return if we have at least a name
            if offer_name and len(offer_name) > 2:
                return {
                    'offer_name': offer_name,
                    'description': description,
                    'price_kr': price_kr,
                    'pickup_delivery': None,
                    'suits_people': None,
                    'available_weekdays': None,
                    'available_hours': None,
                    'availability_text': None
                }
        
        except Exception as e:
            logger.error(f"Error extracting single offer: {e}")
        
        return None
    
    def _is_trio_offer(self, offer: Dict) -> bool:
        """Check if an offer is the TRÍÓ offer"""
        if not offer or not offer.get('offer_name'):
            return False
        
        offer_name = offer['offer_name'].lower()
        # Normalize accented characters for comparison
        offer_name_normalized = offer_name.replace('í', 'i').replace('ó', 'o')
        is_trio = 'trio' in offer_name_normalized
        logger.info(f"Checking if '{offer['offer_name']}' is TRÍÓ offer: {is_trio}")
        return is_trio
    
    def _enhance_trio_offer(self, offer: Dict, base_url: str) -> Dict:
        """Enhance the TRÍÓ offer with specific pizza names"""
        try:
            # Based on the HTML you provided, we know the TRÍÓ pizzas are:
            # - Bistro
            # - Domino's Deluxe  
            # - Kjötveisla
            
            pizza_names = ['Bistro', 'Domino\'s Deluxe', 'Kjötveisla']
            
            # Update the offer description with specific pizza names
            original_desc = offer.get('description', '')
            pizza_list = ', '.join(pizza_names)
            enhanced_desc = f"{original_desc} - Velja á milli: {pizza_list}"
            
            # Create enhanced offer
            enhanced_offer = offer.copy()
            enhanced_offer['description'] = enhanced_desc
            enhanced_offer['trio_pizzas'] = pizza_names  # Store pizza names for frontend use
            
            logger.info(f"Enhanced TRÍÓ offer with pizza names: {pizza_list}")
            return enhanced_offer
            
        except Exception as e:
            logger.error(f"Error enhancing TRÍÓ offer: {e}")
        
        return offer
    
    async def _get_markdown_content(self, url: str) -> str:
        """Get markdown content using crawl4ai"""
        try:
            import crawl4ai as c4a
            
            # Use the correct crawler API
            crawler = c4a.Crawler()
            result = await crawler.arun(
                url=url,
                render_js=True,  # Enable JavaScript rendering
                wait_for="ul.PizzaSelect__list",  # Wait for the pizza list to load
                timeout=30
            )
            
            if result.success:
                return result.markdown
            else:
                logger.error(f"Failed to crawl {url}: {result.error}")
                return ""
                
        except Exception as e:
            logger.error(f"Error getting markdown content: {e}")
            return ""
    
    def _extract_pizza_names_from_content(self, content: str) -> List[str]:
        """Extract pizza names from the markdown content"""
        pizza_names = []
        
        try:
            # First, try to extract pizza names from the specific HTML structure
            # Look for PizzaSelect__title patterns in the content
            import re
            
            # Pattern to match PizzaSelect__title elements
            title_pattern = r'PizzaSelect__title["\']?\s*[>]\s*([^<]+)'
            title_matches = re.findall(title_pattern, content, re.IGNORECASE)
            
            if title_matches:
                # Clean up the matches
                for match in title_matches:
                    pizza_name = match.strip()
                    if pizza_name and len(pizza_name) > 2:
                        pizza_names.append(pizza_name)
                
                # If we found exactly 3 pizzas, that's our TRÍÓ selection
                if len(pizza_names) == 3:
                    logger.info(f"Found 3 pizza names from PizzaSelect__title: {pizza_names}")
                    return pizza_names
            
            # Fallback: Look for specific pizza names mentioned in the HTML
            # Based on the provided HTML structure, we know these are the TRÍÓ pizzas
            expected_pizzas = ['Bistro', 'Domino\'s Deluxe', 'Kjötveisla']
            
            for pizza_name in expected_pizzas:
                if pizza_name.lower() in content.lower():
                    pizza_names.append(pizza_name)
            
            # If we found exactly 3 pizzas, that's likely our TRÍÓ selection
            if len(pizza_names) == 3:
                logger.info(f"Found 3 pizza names from expected list: {pizza_names}")
                return pizza_names
            
            # If we still don't have 3, try a more generic approach
            # Look for patterns that might indicate pizza names
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                # Look for lines that might be pizza names (capitalized, not too long)
                if (len(line) > 3 and len(line) < 50 and 
                    line[0].isupper() and 
                    not any(word in line.lower() for word in ['kr', 'isk', 'price', 'tilboð', 'offer', 'pizza'])):
                    
                    # Check if it looks like a pizza name
                    if any(word in line.lower() for word in ['ostur', 'pepperoni', 'skinka', 'ananas', 'cheddar', 'chili']):
                        pizza_names.append(line)
            
            # Remove duplicates and limit to 3
            pizza_names = list(dict.fromkeys(pizza_names))[:3]
            
            if pizza_names:
                logger.info(f"Extracted pizza names: {pizza_names}")
                return pizza_names
            
        except Exception as e:
            logger.error(f"Error extracting pizza names: {e}")
        
        return []
    
    def enhance_offers_with_food_info(self, offers: List[Dict]) -> List[Dict]:
        """Enhance offers with food information, with special handling for TRÍÓ offer"""
        enhanced_offers = []
        
        for offer in offers:
            enhanced_offer = offer.copy()
            
            # Add basic food information
            enhanced_offer.update(self._get_empty_food_info())
            
            # Special handling for TRÍÓ offer
            if self._is_trio_offer(offer):
                # Enhance TRÍÓ offer if not already enhanced
                if not offer.get('trio_pizzas'):
                    enhanced_offer = self._enhance_trio_offer(enhanced_offer, "")
                
                # Set pizza as the main food type
                enhanced_offer['main_food_type'] = 'pizza'
                trio_pizzas = enhanced_offer.get('trio_pizzas', ['Bistro', "Domino's Deluxe", 'Kjötveisla'])
                enhanced_offer['food_items'] = [
                    {'type': 'pizza', 'name': name, 'category': 'main', 'is_choice': True}
                    for name in trio_pizzas
                ]
                enhanced_offer['food_description'] = f"Velja á milli: {', '.join(trio_pizzas)}"
            else:
                # Use the standard food extraction for other offers
                # Create a temporary offer dict for food extraction
                temp_offer = {
                    'offer_name': offer.get('offer_name', ''),
                    'description': offer.get('description', ''),
                    'restaurant_name': 'Domino\'s Pizza Iceland'
                }
                food_info = self.food_extractor.extract_food_info_batch([temp_offer])[0]
                enhanced_offer.update(food_info)
            
            enhanced_offers.append(enhanced_offer)
        
        return enhanced_offers 