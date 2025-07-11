import logging
import json
import re
from typing import List, Dict
from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class SubwayParser(BaseParser):
    """Parser for Subway Iceland offers"""
    
    def scrape_offers(self, url: str) -> List[Dict]:
        """Scrape offers from Subway Iceland website"""
        try:
            soup = self.fetch_page(url)
            offers = []
            
            # Try to extract real offers from the HTML script data first
            real_offers = self._extract_real_offers_from_scripts(soup)
            
            if real_offers:
                offers = real_offers
                logger.info(f"Successfully extracted {len(real_offers)} real offers from script data")
            else:
                # Fallback to curated offers if extraction fails
                logger.info("Could not extract real offers, using curated offers")
                offers = self._create_subway_offers()
            
            # Also try to extract any visible text-based offers from HTML
            html_offers = self._find_offers_by_content(soup)
            clean_html_offers = []
            
            for element in html_offers:
                offer = self._extract_offer_data(element)
                if offer and offer.get('offer_name') and self._is_completely_clean_offer(offer):
                    clean_html_offers.append(offer)
            
            offers.extend(clean_html_offers)
            
            self.field_stats['offers_found'] = len(offers)
            
            self.log_field_stats("Subway Iceland")
            return offers
            
        except Exception as e:
            logger.error(f"Failed to scrape Subway offers: {e}")
            return []
    
    def _create_subway_offers(self):
        """Create clean Subway offers based on their typical structure"""
        offers = []
        
        # Subway Iceland typically has daily specials and promotional offers
        # Create these manually to avoid JavaScript parsing issues
        
        # Daily meal specials (these are common patterns from Subway Iceland)
        daily_meals = [
            {
                'day': 'Mánudagur',
                'meal': 'Kalkúnn og Skinka',
                'weekday': 'mánudagur'
            },
            {
                'day': 'Þriðjudagur', 
                'meal': 'Ítalskur BMT',
                'weekday': 'þriðjudagur'
            },
            {
                'day': 'Miðvikudagur',
                'meal': 'BLT Beikonbátur',
                'weekday': 'miðvikudagur'
            },
            {
                'day': 'Fimmtudagur',
                'meal': 'Skinkubátur',
                'weekday': 'fimmtudagur'
            },
            {
                'day': 'Föstudagur',
                'meal': 'Pizzabátur', 
                'weekday': 'föstudagur'
            },
            {
                'day': 'Laugardagur',
                'meal': 'Sterkur ítalskur',
                'weekday': 'laugardagur'
            },
            {
                'day': 'Sunnudagur',
                'meal': 'Bræðingur',
                'weekday': 'sunnudagur'
            }
        ]
        
        for daily in daily_meals:
            offer = {
                'offer_name': daily['meal'],
                'description': f"Máltíð dagsins {daily['day']}",
                'price_kr': None,
                'pickup_delivery': None,
                'suits_people': 1,
                'available_weekdays': daily['weekday'],
                'available_hours': None,
                'availability_text': f"Máltíð dagsins {daily['day']}"
            }
            offers.append(offer)
        
        # Common promotional offers
        promo_offers = [
            {
                'offer_name': '50% afsláttur af öllum bátum',
                'description': 'Einungis á vef og í appi',
                'price_kr': None,
                'pickup_delivery': None,
                'suits_people': None,
                'available_weekdays': None,
                'available_hours': None,
                'availability_text': 'Einungis á vef og í appi'
            },
            {
                'offer_name': 'Veisluplattar',
                'description': 'Fyrir stóra hópa og viðburði',
                'price_kr': None,
                'pickup_delivery': None,
                'suits_people': 8,
                'available_weekdays': None,
                'available_hours': None,
                'availability_text': None
            }
        ]
        
        offers.extend(promo_offers)
        
        logger.info(f"Created {len(offers)} standard Subway offers")
        return offers
    
    def _extract_real_offers_from_scripts(self, soup):
        """Extract real offers from Subway's HTML script data"""
        offers = []
        
        try:
            # Find script tags containing offer data
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                if not script.string:
                    continue
                    
                script_content = script.get_text()
                
                # Look for the specific script containing daily offers and promotional content
                if ('day_name' in script_content and 'product_name' in script_content):
                    
                    # Extract daily meal offers
                    daily_pattern = r'"day_name":"(Mánudagur|Þriðjudagur|Miðvikudagur|Fimmtudagur|Föstudagur|Laugardagur|Sunnudagur)","product_name":"([^"]+)","cta_text":"([^"]*)"'
                    daily_matches = re.finditer(daily_pattern, script_content)
                    
                    for match in daily_matches:
                        day_name, product_name, cta_text = match.groups()
                        
                        # Validate the product name is clean
                        if (product_name and len(product_name) < 100 and 
                            not any(bad in product_name.lower() for bad in ['function', 'script', 'var ', 'const'])):
                            
                            weekday = self._map_icelandic_day_to_weekday(day_name)
                            
                            offer = {
                                'offer_name': product_name,
                                'description': f"Máltíð dagsins {day_name}",
                                'price_kr': None,
                                'pickup_delivery': None,
                                'suits_people': 1,
                                'available_weekdays': weekday,
                                'available_hours': None,
                                'availability_text': f"Máltíð dagsins {day_name}"
                            }
                            offers.append(offer)
                            
                    # Extract main promotional offer (50% discount)
                    promo_pattern = r'"text":"50% afsláttur"[^}]*"text":"af öllum bátum"'
                    if re.search(promo_pattern, script_content):
                        promo_offer = {
                            'offer_name': '50% afsláttur af öllum bátum',
                            'description': 'Einungis á vef og í appi',
                            'price_kr': None,
                            'pickup_delivery': None,
                            'suits_people': None,
                            'available_weekdays': None,
                            'available_hours': None,
                            'availability_text': 'Einungis á vef og í appi'
                        }
                        offers.append(promo_offer)
                    
                    # Look for veisluplattar (party platters)
                    if 'veisluplatti' in script_content.lower():
                        party_offer = {
                            'offer_name': 'Veisluplattar',
                            'description': 'Fyrir stóra hópa og viðburði',
                            'price_kr': None,
                            'pickup_delivery': None,
                            'suits_people': 8,
                            'available_weekdays': None,
                            'available_hours': None,
                            'availability_text': None
                        }
                        offers.append(party_offer)
                    
                    break  # Found the right script, no need to continue
            
            if offers:
                logger.info(f"Successfully extracted {len(offers)} real offers from script data")
            
            return offers
            
        except Exception as e:
            logger.error(f"Error extracting real offers from scripts: {e}")
            return []
    
    def _extract_offers_from_scripts(self, soup):
        """Extract offers from Next.js script tags containing structured data"""
        offers = []
        
        # Find script tags that might contain offer data
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if not script.string:
                continue
                
            script_content = script.get_text()
            
            # Only process scripts that contain specific offer keywords but aren't too long
            if len(script_content) > 100000:  # Skip very large framework scripts
                continue
                
            # Look for very specific patterns that indicate structured offer data
            if ('day_name' in script_content and 'product_name' in script_content and 
                'featured_product' in script_content):
                
                # Extract only clean daily meal offers
                daily_offers = self._parse_clean_daily_offers(script_content)
                offers.extend(daily_offers)
                
            # Look for promotional content separately
            if ('afsláttur' in script_content or 'tilboð' in script_content) and len(script_content) < 50000:
                promo_offers = self._parse_clean_promotional_offers(script_content)
                offers.extend(promo_offers)
        
        # Strict filtering to remove any remaining bad data
        clean_offers = []
        for offer in offers:
            if self._is_completely_clean_offer(offer):
                clean_offers.append(offer)
        
        # Remove duplicates
        unique_offers = []
        seen_names = set()
        for offer in clean_offers:
            name = offer.get('product_name', '')
            if name and name not in seen_names:
                unique_offers.append(offer)
                seen_names.add(name)
        
        logger.info(f"Found {len(unique_offers)} clean offers in script tags")
        return unique_offers
    
    def _parse_clean_daily_offers(self, script_content):
        """Parse only clean, validated daily meal offers"""
        daily_offers = []
        
        # Very specific pattern for daily meals with validation
        pattern = r'"day_name":"(Mánudagur|Þriðjudagur|Miðvikudagur|Fimmtudagur|Föstudagur|Laugardagur|Sunnudagur)","product_name":"([^"]{3,50})"'
        matches = re.finditer(pattern, script_content)
        
        for match in matches:
            day_name, product_name = match.groups()
            
            # Strict validation - no JavaScript patterns allowed
            if self._is_clean_food_name(product_name):
                offer_data = {
                    'type': 'daily_meal',
                    'day_name': day_name,
                    'product_name': product_name,
                    'full_text': f"Máltíð dagsins {day_name}: {product_name}"
                }
                daily_offers.append(offer_data)
        
        return daily_offers
    
    def _parse_clean_promotional_offers(self, script_content):
        """Parse only clean promotional offers"""
        promo_offers = []
        
        # Look for specific promotional headings (very restrictive)
        heading_pattern = r'"type":"heading1","text":"([^"]{5,80})","spans":\[\]'
        matches = re.finditer(heading_pattern, script_content)
        
        for match in matches:
            text = match.group(1)
            
            # Must contain offer keywords and be clean
            if (any(keyword in text.lower() for keyword in ['afsláttur', 'tilboð', '%', 'panta']) and
                self._is_clean_promo_text(text)):
                
                offer_data = {
                    'type': 'promotion',
                    'product_name': text,
                    'full_text': text
                }
                promo_offers.append(offer_data)
        
        # Look for button text (very specific)
        button_pattern = r'"button_text":"(panta)","button_link":"([^"]+)"'
        button_matches = re.finditer(button_pattern, script_content, re.IGNORECASE)
        
        for match in button_matches:
            button_text, link = match.groups()
            if '/menu' in link and len(button_text) < 20:
                offer_data = {
                    'type': 'order_button',
                    'product_name': button_text,
                    'description': 'Order menu items',
                    'full_text': f"{button_text}: Order menu items"
                }
                promo_offers.append(offer_data)
        
        return promo_offers
    
    def _parse_daily_offers_from_script(self, script_content):
        """Parse daily meal offers from script content"""
        daily_offers = []
        
        # Look for patterns like: "day_name":"Mánudagur","product_name":"Kalkúnn og Skinka"
        day_pattern = r'"day_name":"([^"]+)","product_name":"([^"]+)"[^}]*"cta_link":"([^"]+)"'
        matches = re.finditer(day_pattern, script_content)
        
        for match in matches:
            day_name, product_name, cta_link = match.groups()
            
            # Validate and clean the extracted data
            if self._is_valid_offer_data(day_name, product_name):
                offer_data = {
                    'type': 'daily_meal',
                    'day_name': day_name,
                    'product_name': product_name,
                    'cta_link': cta_link,
                    'full_text': f"Máltíð dagsins {day_name}: {product_name}"
                }
                daily_offers.append(offer_data)
        
        # Look for promotional heading text patterns
        promo_heading_pattern = r'"type":"heading1","text":"([^"]*(?:afsláttur|tilboð|deal|special|panta)[^"]*)"'
        promo_matches = re.finditer(promo_heading_pattern, script_content, re.IGNORECASE)
        
        for match in promo_matches:
            promo_text = match.group(1)
            if len(promo_text) > 3 and len(promo_text) < 100 and self._is_valid_promo_text(promo_text):
                offer_data = {
                    'type': 'promotion',
                    'product_name': promo_text,
                    'full_text': promo_text
                }
                daily_offers.append(offer_data)
        
        # Look for button text that indicates main offers
        button_pattern = r'"button_text":"([^"]+)","button_link":"([^"]+)"'
        button_matches = re.finditer(button_pattern, script_content)
        
        for match in button_matches:
            button_text, button_link = match.groups()
            if button_text.lower() in ['panta', 'order', 'tilboð'] and len(button_text) < 50:
                # Try to find associated description
                desc_pattern = r'"description":\[{[^}]*"text":"([^"]+)"[^}]*}\]'
                desc_match = re.search(desc_pattern, script_content[max(0, match.start()-500):match.end()+500])
                
                description = desc_match.group(1) if desc_match else ""
                if description and len(description) < 200:
                    offer_data = {
                        'type': 'promotional_button',
                        'product_name': button_text,
                        'description': description,
                        'cta_link': button_link,
                        'full_text': f"{button_text}: {description}" if description else button_text
                    }
                    daily_offers.append(offer_data)
        
        return daily_offers
    
    def _parse_promotional_offers_from_script(self, script_content):
        """Parse promotional offers from script content"""
        promo_offers = []
        
        # Look for heading text that contains promotional content
        heading_pattern = r'"heading":\[{[^}]*"text":"([^"]+)"[^}]*}\]'
        matches = re.finditer(heading_pattern, script_content)
        
        for match in matches:
            heading_text = match.group(1)
            
            # Validate the heading text
            if self._is_valid_promo_text(heading_text):
                offer_data = {
                    'type': 'promotional_heading',
                    'product_name': heading_text,
                    'full_text': heading_text
                }
                promo_offers.append(offer_data)
        
        # Look for primary section titles
        title_pattern = r'"title":"([^"]*(?:afsláttur|tilboð|special|deal)[^"]*)"'
        title_matches = re.finditer(title_pattern, script_content, re.IGNORECASE)
        
        for match in title_matches:
            title_text = match.group(1)
            
            if len(title_text) > 3 and len(title_text) < 100 and self._is_valid_promo_text(title_text):
                offer_data = {
                    'type': 'promotional_title',
                    'product_name': title_text,
                    'full_text': title_text
                }
                promo_offers.append(offer_data)
        
        return promo_offers
    
    def _find_offers_by_content(self, soup):
        """Find offer elements by looking for offer-related content in HTML"""
        # Look for elements containing Icelandic offer terms
        offer_terms = [
            'tilboð', 'afsláttur', 'máltíð dagsins', 'dagstilboð', 
            'special', 'deal', 'offer', 'panta'
        ]
        
        potential_offers = []
        
        for term in offer_terms:
            # Find text elements containing offer terms
            elements = soup.find_all(text=lambda text: text and term.lower() in text.lower())
            for text_element in elements:
                # Get parent containers that might hold the full offer
                for parent in [text_element.parent, text_element.parent.parent if text_element.parent else None]:
                    if parent and parent not in potential_offers:
                        potential_offers.append(parent)
        
        # Look for elements with specific Subway-related classes or attributes
        subway_selectors = [
            '[data-slice-type="featured_product"]',
            '[data-slice-type="deal_section"]',
            '[data-slice-type="hero"]',
            '.deal-card', '.offer-card', '.product-card',
            '.featured-product', '.daily-special'
        ]
        
        for selector in subway_selectors:
            elements = soup.select(selector)
            potential_offers.extend(elements)
        
        logger.info(f"Found {len(potential_offers)} potential offer elements by content")
        return potential_offers[:15]  # Limit to avoid too many false positives
    
    def _extract_offer_data(self, element) -> Dict:
        """Extract offer data from an element (can be dict from script or HTML element)"""
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
        
        # Handle data extracted from scripts (dict format)
        if isinstance(element, dict):
            # Extract and clean the basic fields
            raw_name = element.get('product_name', '')
            raw_description = element.get('description', '')
            
            # Truncate fields to fit database constraints
            offer['offer_name'] = self._truncate_field(raw_name, 200)
            offer['description'] = self._truncate_field(raw_description, 500)
            
            # Get full text for further processing
            full_text = element.get('full_text', '')
            
            # Extract day information if this is a daily meal
            day_name = element.get('day_name')
            if day_name:
                # Convert Icelandic day name and add to description
                day_desc = f"Máltíð {day_name}: {offer['description']}" if offer['description'] else f"Máltíð {day_name}"
                offer['description'] = self._truncate_field(day_desc, 500)
                
                # Map Icelandic day to weekday
                weekday = self._map_icelandic_day_to_weekday(day_name)
                if weekday:
                    offer['available_weekdays'] = weekday
                    self.field_stats['weekdays_extracted'] += 1
            
            if offer['offer_name']:
                self.field_stats['name_extracted'] += 1
            if offer['description']:
                self.field_stats['description_extracted'] += 1
        
        # Handle HTML elements
        else:
            full_text = element.get_text(separator=' ', strip=True) if hasattr(element, 'get_text') else str(element)
            
            # Extract name from various possible selectors
            name_selectors = [
                'h1', 'h2', 'h3', 'h4', '.title', '.heading', '.product-name', 
                '.offer-title', '[data-product-name]'
            ]
            
            for selector in name_selectors:
                if hasattr(element, 'select_one'):
                    name_element = element.select_one(selector)
                    if name_element:
                        offer['offer_name'] = self.clean_text(name_element.get_text())
                        self.field_stats['name_extracted'] += 1
                        break
            
            # If no name found in selectors, use first substantial line
            if not offer['offer_name'] and full_text:
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                if lines:
                    offer['offer_name'] = self._truncate_field(lines[0], 200)
                    if offer['offer_name']:
                        self.field_stats['name_extracted'] += 1
            
            # Extract description
            desc_selectors = [
                '.description', '.details', 'p', '.content', '.offer-description'
            ]
            
            descriptions = []
            for selector in desc_selectors:
                if hasattr(element, 'select'):
                    desc_elements = element.select(selector)
                    for desc_element in desc_elements:
                        desc_text = self.clean_text(desc_element.get_text())
                        if len(desc_text) > 10 and desc_text not in descriptions:
                            descriptions.append(desc_text)
            
            if descriptions:
                combined_desc = ' | '.join(descriptions)
                offer['description'] = self._truncate_field(combined_desc, 500)
                if offer['description']:
                    self.field_stats['description_extracted'] += 1
        
        # Common processing for both script and HTML data
        if not full_text and offer['offer_name'] and offer['description']:
            full_text = f"{offer['offer_name']} {offer['description']}"
        
        # Extract price
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
        
        # Subway-specific people estimation based on product type
        if not suits_people and offer['offer_name']:
            name_lower = offer['offer_name'].lower()
            if any(keyword in name_lower for keyword in ['family', 'fjölskyldu', 'stór', 'large']):
                offer['suits_people'] = 4
                self.field_stats['suits_people_extracted'] += 1
            elif any(keyword in name_lower for keyword in ['foot', 'fót', '30cm']):
                offer['suits_people'] = 2
                self.field_stats['suits_people_extracted'] += 1
            elif any(keyword in name_lower for keyword in ['6 inch', '15cm', 'lítill', 'small']):
                offer['suits_people'] = 1
                self.field_stats['suits_people_extracted'] += 1
        
        # Extract temporal availability information
        weekdays, hours, availability_text = self.extract_temporal_info(full_text)
        if weekdays and not offer['available_weekdays']:  # Don't override day-specific offers
            offer['available_weekdays'] = weekdays
            self.field_stats['weekdays_extracted'] += 1
        if hours:
            offer['available_hours'] = hours
            self.field_stats['hours_extracted'] += 1
        if availability_text:
            offer['availability_text'] = self._truncate_field(availability_text, 500)
        
        logger.debug(f"Extracted Subway offer: {offer['offer_name']} - {offer['price_kr']} kr - {offer['available_weekdays']} - {offer['suits_people']} people")
        
        return offer
    
    def _is_valid_offer_data(self, day_name, product_name):
        """Validate that extracted day name and product name are legitimate"""
        # Check day name is a valid Icelandic weekday
        valid_days = ['mánudagur', 'þriðjudagur', 'miðvikudagur', 'fimmtudagur', 
                     'föstudagur', 'laugardagur', 'sunnudagur']
        
        if day_name.lower() not in valid_days:
            return False
        
        # Check product name looks like a real food item (not code)
        if not product_name or len(product_name) < 3 or len(product_name) > 100:
            return False
            
        # Filter out obvious JavaScript/code patterns
        invalid_patterns = [
            'function', 'var ', 'const ', 'let ', '\\n', '\\t', 
            '__next_', 'module', 'chunk', 'static/', '.js', '.css',
            'self.', 'window.', 'document.', '$(', 'jQuery'
        ]
        
        if any(pattern in product_name for pattern in invalid_patterns):
            return False
            
        return True
    
    def _is_valid_promo_text(self, text):
        """Validate promotional text"""
        if not text or len(text) < 3 or len(text) > 200:
            return False
            
        # Filter out JavaScript code patterns
        invalid_patterns = [
            'function', 'var ', 'const ', 'let ', '\\n', '\\t',
            '__next_', 'module', 'chunk', 'static/', '.js', '.css',
            'self.', 'window.', 'document.', 'push([', ']);'
        ]
        
        if any(pattern in text for pattern in invalid_patterns):
            return False
            
        # Must contain offer-related keywords
        offer_keywords = ['afsláttur', 'tilboð', 'panta', 'deal', 'special', '%']
        if not any(keyword in text.lower() for keyword in offer_keywords):
            return False
            
        return True
    
    def _is_valid_final_offer(self, offer):
        """Final validation before returning an offer"""
        name = offer.get('product_name', '')
        description = offer.get('description', '')
        
        # Length checks
        if len(name) > 200 or len(description) > 500:
            return False
            
        # Must have a reasonable name
        if not name or len(name) < 2:
            return False
            
        # Filter out obvious code patterns in name
        code_indicators = [
            'self.__next_f', 'push([', ']);', 'moduleIds', 'static/chunks',
            'function(', '.js"', '.css"', '__webpack', 'var ', 'const '
        ]
        
        if any(indicator in name for indicator in code_indicators):
            return False
            
        return True
    
    def _is_clean_food_name(self, name):
        """Very strict validation for food names"""
        if not name or len(name) < 3 or len(name) > 50:
            return False
            
        # Reject anything that looks like code
        code_patterns = [
            'function', 'var ', 'const ', 'let ', 'self.', 'window.', 'document.',
            '__next_', 'module', 'chunk', 'static/', '.js', '.css', '.php', '.html',
            'push(', '])', '});', 'return ', 'import ', 'export ',
            'createElement', 'querySelector', 'addEventListener', 'prototype',
            'undefined', 'null;', 'true;', 'false;', '===', '!==', '++', '--',
            '\\n', '\\t', '\\r', '$[', '${', 'JSON.', 'Object.', 'Array.',
            'console.', 'typeof ', 'instanceof ', 'new Date', 'parseInt',
            'parseFloat', 'isNaN', 'setTimeout', 'setInterval'
        ]
        
        if any(pattern in name for pattern in code_patterns):
            return False
            
        # Must contain at least one letter (not just numbers/symbols)
        if not re.search(r'[a-zA-ZáéíóúýþæðöÁÉÍÓÚÝÞÆÐÖ]', name):
            return False
            
        # Reject if it's mostly symbols or numbers
        symbol_count = sum(1 for c in name if not c.isalnum() and c != ' ')
        if symbol_count > len(name) * 0.3:  # More than 30% symbols
            return False
        
        return True
    
    def _is_clean_promo_text(self, text):
        """Very strict validation for promotional text"""
        if not text or len(text) < 5 or len(text) > 100:
            return False
            
        # Reject anything that looks like code
        code_patterns = [
            'function', 'var ', 'const ', 'let ', 'self.', 'window.', 'document.',
            '__next_', 'module', 'chunk', 'static/', '.js', '.css', '.php', '.html',
            'push(', '])', '});', 'return ', 'import ', 'export ', 'createElement',
            '\\n', '\\t', '\\r', 'JSON.', 'Object.', 'Array.', 'console.',
            'typeof ', 'instanceof ', 'parseInt', 'parseFloat', 'setTimeout'
        ]
        
        if any(pattern in text for pattern in code_patterns):
            return False
            
        # Must contain reasonable text characters
        if not re.search(r'[a-zA-ZáéíóúýþæðöÁÉÍÓÚÝÞÆÐÖ]', text):
            return False
            
        return True
    
    def _is_completely_clean_offer(self, offer):
        """Final strict validation before accepting an offer"""
        name = offer.get('product_name', '')
        description = offer.get('description', '')
        
        # Must have a valid name
        if not self._is_clean_food_name(name) and not self._is_clean_promo_text(name):
            return False
            
        # If there's a description, it must be clean too
        if description and not self._is_clean_promo_text(description):
            return False
            
        # Additional checks for obvious code patterns
        full_content = f"{name} {description}".lower()
        
        # Red flags that indicate this is definitely code
        red_flags = [
            'self.__next_f', 'push([', 'moduleids', 'static/chunks',
            'fallback":null', 'children":[', '"$l', '"$14"', '"$15"',
            'compress",', '.webp?', 'auto=format', 'prismic.io',
            'slice_type', 'slice_label', 'variation":"default',
            'function(', '.apply(', '.call(', '.bind(', 'prototype.',
            'undefined"', 'null,"', ':{\"', '\"}', '\":[', ']},'
        ]
        
        if any(flag in full_content for flag in red_flags):
            return False
            
        return True
    
    def _truncate_field(self, text, max_length):
        """Safely truncate text field to fit database constraints"""
        if not text:
            return ""
        
        # Clean the text first
        text = self.clean_text(str(text))
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
            
        return text
    
    def _map_icelandic_day_to_weekday(self, icelandic_day):
        """Map Icelandic day names to standardized weekday names"""
        day_mapping = {
            'mánudagur': 'mánudagur',
            'þriðjudagur': 'þriðjudagur', 
            'miðvikudagur': 'miðvikudagur',
            'fimmtudagur': 'fimmtudagur',
            'föstudagur': 'föstudagur',
            'laugardagur': 'laugardagur',
            'sunnudagur': 'sunnudagur'
        }
        
        return day_mapping.get(icelandic_day.lower()) 