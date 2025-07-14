import logging
from typing import List, Dict
from .base_parser import BaseParser
import re, json as pyjson

logger = logging.getLogger(__name__)


class KFCParser(BaseParser):
    """Parser for KFC Iceland offers"""
    
    def scrape_offers(self, url: str) -> List[Dict]:
        """Scrape offers from KFC Iceland offers page"""
        try:
            soup = self.fetch_page(url)
            offers = []

            # --- NEW: Build product_id -> price mapping from script blocks ---
            product_price_map = {}
            for script in soup.find_all('script', string=True):
                script_text = script.string
                if not script_text:
                    continue
                match = re.search(r"Product\.setBasePricing\('([^']+)',\s*(\{.*?\})\);", script_text)
                if match:
                    product_id = match.group(1)
                    data = match.group(2)
                    try:
                        data_json = pyjson.loads(data.replace("'", '"'))
                        price = None
                        if 'skus' in data_json and '' in data_json['skus']:
                            price = data_json['skus']['']
                        if price:
                            product_price_map[product_id] = price
                    except Exception:
                        continue
            # --- END NEW ---

            # KFC Iceland specific selectors for TILBOÐ sections only
            # Look for category sections that contain "tilboð" in their ID or heading
            tilbod_sections = []
            
            # Method 1: Find sections by ID containing "tilbod"
            sections_by_id = soup.find_all('div', class_='category__subcategory', id=lambda x: x and 'tilbod' in x.lower())
            tilbod_sections.extend(sections_by_id)
            
            # Method 2: Find sections by heading text containing "TILBOÐ"
            tilbod_headings = soup.find_all('h3', class_='category__subcategory-title')
            for heading in tilbod_headings:
                heading_text = heading.get_text().strip()
                if 'TILBOÐ' in heading_text.upper():
                    # Get the parent section
                    section = heading.find_parent('div', class_='category__subcategory')
                    if section and section not in tilbod_sections:
                        tilbod_sections.append(section)
            
            logger.info(f"Found {len(tilbod_sections)} Tilboð sections")
            
            # Extract products only from Tilboð sections
            offer_elements = []
            for section in tilbod_sections:
                section_id = section.get('id', 'unknown')
                section_title = section.find('h3', class_='category__subcategory-title')
                section_name = section_title.get_text().strip() if section_title else 'Unknown'
                
                # Find products within this section
                products_container = section.find('div', class_='category__products')
                if products_container:
                    products = products_container.find_all('div', class_='product')
                    offer_elements.extend(products)
                    logger.info(f"Found {len(products)} products in section '{section_name}' ({section_id})")
            
            # Fallback: if no tilboð sections found, try the old method but with a warning
            if not offer_elements:
                logger.warning("No Tilboð sections found, falling back to content-based search")
                offer_elements = self._find_offers_by_content(soup)
            
            if not offer_elements:
                logger.warning("No product elements found in KFC Tilboð sections")
                return offers
            
            self.field_stats['offers_found'] = len(offer_elements)
            logger.info(f"Total offer products to process: {len(offer_elements)}")
            
            for element in offer_elements:
                offer = self._extract_offer_data(element, product_price_map)
                if offer and offer.get('offer_name'):
                    offers.append(offer)
            
            self.log_field_stats("KFC Iceland")
            return offers
            
        except Exception as e:
            logger.error(f"Failed to scrape KFC offers: {e}")
            return []
    
    def _find_offers_by_content(self, soup):
        """Find offer elements by looking for offer-related content"""
        # Look for elements containing Icelandic food terms, but still try to limit scope
        food_terms = ['kjúklingur', 'kjukling', 'borgari', 'borgar', 'maltid', 'máltíð', 'bucket', 'pakki']
        
        potential_offers = []
        for term in food_terms:
            # Find elements containing food terms
            elements = soup.find_all(text=lambda text: text and term.lower() in text.lower())
            for text_element in elements:
                # Get the parent container that might hold the full offer
                parent = text_element.parent
                while parent and not parent.get('class'):
                    parent = parent.parent
                    
                # Check if this element is within a category__products container (more likely to be an offer)
                if parent and parent.find_parent('div', class_='category__products'):
                    product_container = parent.find_parent('div', class_='product')
                    if product_container and product_container not in potential_offers:
                        potential_offers.append(product_container)
        
        logger.info(f"Found {len(potential_offers)} potential product elements by content")
        return potential_offers[:30]  # Limit to avoid too many false positives
    
    def _extract_offer_data(self, element, product_price_map=None) -> Dict:
        """Extract offer data from a single product element"""
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
        
        # --- NEW: Try to get product_id from form or container ---
        product_id = None
        form = element.find('form', {'data-product': True})
        if form:
            product_id = form.get('data-product')
        if not product_id and element.get('id') and element.get('id').startswith('product_'):
            product_id = element.get('id').replace('product_', '')
        # --- END NEW ---

        # Extract name using KFC specific selectors
        name_selectors = [
            '.product__name-wrapper',  # KFC specific name wrapper
            '.product__name',  # KFC product name container
            'h4',  # Generic header fallback
            '.title', '.name'  # Generic fallbacks
        ]
        
        for selector in name_selectors:
            name_element = element.select_one(selector)
            if name_element:
                name_text = self.clean_text(name_element.get_text())
                # Filter out empty text and unwanted elements
                if name_text and len(name_text) > 2 and 'setja í körfu' not in name_text.lower():
                    offer['offer_name'] = name_text
                    self.field_stats['name_extracted'] += 1
                    break
        
        # Extract description using KFC specific selectors
        description_selectors = [
            '.product__description p',  # KFC specific description
            '.product__description',    # KFC description container
            '.description', 'p',       # Generic fallbacks
            '.content', '.details'     # More generic fallbacks
        ]
        
        descriptions = []
        for selector in description_selectors:
            desc_elements = element.select(selector)
            for desc_element in desc_elements:
                desc_text = self.clean_text(desc_element.get_text())
                if len(desc_text) > 15 and desc_text not in descriptions:  # Substantial descriptions only
                    descriptions.append(desc_text)
        
        if descriptions:
            # Join multiple description parts and clean up
            combined_desc = ' '.join(descriptions)
            offer['description'] = self.clean_text(combined_desc)
            self.field_stats['description_extracted'] += 1
        
        # --- NEW: Use product_price_map if available ---
        if product_price_map and product_id and product_id in product_price_map:
            price = product_price_map[product_id]
            if price:
                offer['price_kr'] = int(round(price / 100))
                self.field_stats['price_extracted'] += 1
        else:
            # fallback to old extraction
            price_selectors = [
                '.product__price',           # KFC specific price
                '.product__mobile-price-value',  # KFC mobile price
                '[data-product-price]',      # KFC price data attribute
                '.price'                     # Generic fallback
            ]
            for selector in price_selectors:
                price_elements = element.select(selector)
                for price_element in price_elements:
                    price_text = price_element.get_text()
                    # Handle KFC specific format: "kr&nbsp;2299" or "kr 2299"
                    price = self.extract_price_kr(price_text)
                    if price:
                        # KFC-specific fix: if price is less than 1000, multiply by 10 (missing trailing zero)
                        if price < 1000:
                            price = price * 10
                        offer['price_kr'] = price
                        self.field_stats['price_extracted'] += 1
                        break
                if offer['price_kr']:
                    break
        # --- END NEW ---
        
        # Get all text for additional extraction
        full_text = element.get_text(separator=' ', strip=True)
        
        # Extract pickup/delivery info (KFC might show delivery options)
        pickup_delivery = self.extract_pickup_delivery(full_text)
        if pickup_delivery:
            offer['pickup_delivery'] = pickup_delivery
            self.field_stats['pickup_delivery_extracted'] += 1
        
        # Extract number of people it suits (look for Icelandic patterns)
        suits_people = self.extract_suits_people(full_text)
        if suits_people:
            offer['suits_people'] = suits_people
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
        
        logger.debug(f"Extracted KFC product: {offer['offer_name']} - {offer['price_kr']} kr - {offer['available_weekdays']} - {offer['available_hours']}")
        
        return offer 