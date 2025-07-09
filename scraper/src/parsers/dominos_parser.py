import logging
from typing import List, Dict
from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class DominosParser(BaseParser):
    """Parser for Domino's Pizza Iceland offers"""
    
    def scrape_offers(self, url: str) -> List[Dict]:
        """Scrape offers from Domino's Pizza Iceland offers page"""
        try:
            soup = self.fetch_page(url)
            offers = []
            
            # Domino's specific selectors based on actual HTML structure
            # Primary selectors for the current Domino's Iceland website
            primary_selectors = [
                '.OfferCard__listItem',  # Main offer card containers
                '[class*="OfferCard"]',  # Any class containing OfferCard
                '.offer-card',           # Alternative naming
                '.offer-item'            # Fallback
            ]
            
            # Fallback selectors if the primary ones don't work
            fallback_selectors = [
                '.deal-card',
                '.promotion-item',
                '.pizza-deal',
                '.special-offer',
                '.menu-item',
                '[data-deal]',
                '.product-card'
            ]
            
            offer_elements = []
            
            # Try primary selectors first
            for selector in primary_selectors:
                elements = soup.select(selector)
                if elements:
                    offer_elements = elements
                    logger.info(f"Found {len(elements)} offers using primary selector: {selector}")
                    break
            
            # If primary selectors don't work, try fallback selectors
            if not offer_elements:
                for selector in fallback_selectors:
                    elements = soup.select(selector)
                    if elements:
                        offer_elements = elements
                        logger.info(f"Found {len(elements)} offers using fallback selector: {selector}")
                        break
            
            # If no specific offer selectors work, try to find elements with offer-related text
            if not offer_elements:
                offer_elements = self._find_offers_by_content(soup)
            
            if not offer_elements:
                logger.warning("No offer elements found on Domino's page")
                return offers
            
            self.field_stats['offers_found'] = len(offer_elements)
            
            for element in offer_elements:
                offer = self._extract_offer_data(element)
                if offer and offer.get('offer_name'):
                    offers.append(offer)
            
            self.log_field_stats("Domino's Pizza Iceland")
            return offers
            
        except Exception as e:
            logger.error(f"Failed to scrape Domino's offers: {e}")
            return []
    
    def _find_offers_by_content(self, soup):
        """Find offer elements by looking for offer-related content"""
        # Look for elements containing offer-related terms (including Icelandic)
        offer_terms = ['tilboð', 'tilbod', 'offer', 'deal', 'special', 'combo', 'pizza', 'meal']
        
        potential_offers = []
        for term in offer_terms:
            # Find elements containing offer terms
            elements = soup.find_all(text=lambda text: text and term.lower() in text.lower())
            for text_element in elements:
                # Get the parent container that might hold the full offer
                for parent in [text_element.parent, text_element.parent.parent if text_element.parent else None]:
                    if parent and parent not in potential_offers:
                        potential_offers.append(parent)
        
        # Also look for price indicators
        price_elements = soup.find_all(text=lambda text: text and 'kr' in text.lower())
        for text_element in price_elements:
            for parent in [text_element.parent, text_element.parent.parent if text_element.parent else None]:
                if parent and parent not in potential_offers:
                    potential_offers.append(parent)
        
        logger.info(f"Found {len(potential_offers)} potential offer elements by content")
        return potential_offers[:20]  # Limit to avoid too many false positives
    
    def _extract_offer_data(self, element) -> Dict:
        """Extract offer data from a single offer element"""
        offer = {
            'offer_name': None,
            'description': None,
            'price_kr': None,
            'pickup_delivery': None,
            'suits_people': None,
            'available_weekdays': None,
            'available_hours': None,
            'availability_text': None
        }
        
        # Get all text from the element and its children
        full_text = element.get_text(separator=' ', strip=True)
        
        # Extract name using Domino's specific selectors
        name_selectors = [
            '.Card__title',         # Domino's specific title class
            '[class*="Card__title"]', # Any class containing Card__title
            '.card-title',          # Alternative naming
            'h1', 'h2', 'h3', 'h4', # Standard headers
            '.title', '.name', '.product-name', '.deal-name', '[data-name]'  # Fallback
        ]
        
        for selector in name_selectors:
            name_element = element.select_one(selector)
            if name_element:
                offer['offer_name'] = self.clean_text(name_element.get_text())
                self.field_stats['name_extracted'] += 1
                logger.debug(f"Found name using selector {selector}: {offer['offer_name']}")
                break
        
        # If no name found in specific selectors, try to extract from full text
        if not offer['offer_name']:
            # Look for the first substantial text that might be a name
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            if lines:
                # For Domino's, often the first line is the pizza/deal name
                offer['offer_name'] = lines[0]
                self.field_stats['name_extracted'] += 1
                logger.debug(f"Found name from first line: {offer['offer_name']}")
        
        # Extract description using Domino's specific selectors
        description_selectors = [
            '.Card__details',       # Domino's specific details class
            '[class*="Card__details"]', # Any class containing Card__details
            '.card-details',        # Alternative naming
            '.description', '.details', '.ingredients', 'p', '.content'  # Fallback
        ]
        
        descriptions = []
        for selector in description_selectors:
            desc_elements = element.select(selector)
            for desc_element in desc_elements:
                desc_text = self.clean_text(desc_element.get_text())
                if len(desc_text) > 10 and desc_text not in descriptions:  # Avoid duplicates
                    descriptions.append(desc_text)
        
        if descriptions:
            # Join descriptions and clean up
            full_description = ' | '.join(descriptions)
            # Remove offer name from description if it appears at the beginning
            if offer['offer_name'] and full_description.startswith(offer['offer_name']):
                full_description = full_description[len(offer['offer_name']):].strip()
            offer['description'] = self.clean_text(full_description)
            self.field_stats['description_extracted'] += 1
        elif len(full_text) > 50:
            # Use full text minus the name as fallback
            description_text = full_text
            if offer['offer_name']:
                # More thorough cleaning: remove the offer name from anywhere in the text
                description_text = description_text.replace(offer['offer_name'], '', 1).strip()
                # Also remove it if it appears with common separators
                for separator in [' - ', ': ', ' | ']:
                    pattern = offer['offer_name'] + separator
                    if description_text.startswith(pattern):
                        description_text = description_text[len(pattern):].strip()
                        break
            offer['description'] = self.clean_text(description_text)
            self.field_stats['description_extracted'] += 1
        
        # Extract price using Domino's specific selectors
        price_selectors = [
            '.OfferCard__price',    # Domino's specific price class
            '[class*="OfferCard__price"]', # Any class containing OfferCard__price
            '.offer-price',         # Alternative naming
            '.price', '.cost', '[data-price]'  # Fallback
        ]
        
        price = None
        for selector in price_selectors:
            price_element = element.select_one(selector)
            if price_element:
                price_text = price_element.get_text()
                price = self.extract_price_kr(price_text)
                if price:
                    logger.debug(f"Found price using selector {selector}: {price} kr")
                    break
        
        # If no price found in specific selectors, extract from full text
        if not price:
            price = self.extract_price_kr(full_text)
        
        if price:
            offer['price_kr'] = price
            self.field_stats['price_extracted'] += 1
        
        # Extract pickup/delivery info
        pickup_delivery = self.extract_pickup_delivery(full_text)
        if pickup_delivery:
            offer['pickup_delivery'] = pickup_delivery
            self.field_stats['pickup_delivery_extracted'] += 1
        
        # Extract number of people it suits
        suits_people = self.extract_suits_people(full_text)
        if suits_people:
            offer['suits_people'] = suits_people
            self.field_stats['suits_people_extracted'] += 1
        
        # Domino's specific logic for pizza size/people
        if not suits_people and 'pizza' in full_text.lower():
            # Try to infer from pizza size or offer type
            if any(keyword in full_text.lower() for keyword in ['large', 'stór', 'family', 'hóp', 'group']):
                offer['suits_people'] = 4
                self.field_stats['suits_people_extracted'] += 1
            elif any(keyword in full_text.lower() for keyword in ['medium', 'miðlungs', 'tríó', 'trio']):
                offer['suits_people'] = 3
                self.field_stats['suits_people_extracted'] += 1
            elif any(keyword in full_text.lower() for keyword in ['tvenn', 'double', 'two', 'pair']):
                offer['suits_people'] = 2
                self.field_stats['suits_people_extracted'] += 1
            elif any(keyword in full_text.lower() for keyword in ['small', 'lítil', 'hádegis', 'lunch']):
                offer['suits_people'] = 1
                self.field_stats['suits_people_extracted'] += 1
        
        # Extract temporal availability information (NEW)
        weekdays, hours, availability_text = self.extract_temporal_info(full_text)
        if weekdays:
            offer['available_weekdays'] = weekdays
            self.field_stats['weekdays_extracted'] += 1
        if hours:
            offer['available_hours'] = hours
            self.field_stats['hours_extracted'] += 1
        if availability_text:
            offer['availability_text'] = availability_text
        
        logger.debug(f"Extracted offer: {offer['offer_name']} - {offer['price_kr']} kr - {offer['suits_people']} people - {offer['available_weekdays']} - {offer['available_hours']}")
        
        return offer 