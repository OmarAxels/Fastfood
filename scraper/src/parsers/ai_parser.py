import logging
import json
import asyncio
from typing import List, Dict
from .base_parser import BaseParser
import g4f
from crawl4ai import AsyncWebCrawler
from config import AI_MODEL

logger = logging.getLogger(__name__)


class AIParser(BaseParser):
    """AI-powered parser that uses crawl4ai and g4f for offer extraction"""
    
    def __init__(self):
        super().__init__()
        self.crawler = None
    
    async def _get_markdown_content(self, url: str) -> str:
        """Get markdown content from URL using crawl4ai"""
        try:
            # Configure crawler with specific settings to avoid encoding issues
            crawler_config = {
                'verbose': False,
                'headless': True,
                'browser_type': 'chromium'
            }
            
            async with AsyncWebCrawler(**crawler_config) as crawler:
                result = await crawler.arun(
                    url=url,
                    wait_for_selector="body",
                    timeout=30
                )
                
                if not result or not result.markdown:
                    logger.warning(f"No markdown content found for {url}")
                    return ""
                
                # Clean markdown content to avoid encoding issues
                markdown_content = result.markdown
                
                # Replace problematic Unicode characters
                replacements = {
                    '\u2192': '->',
                    '\u2190': '<-',
                    '\u2013': '-',
                    '\u2014': '--',
                    '\u2019': "'",
                    '\u201c': '"',
                    '\u201d': '"',
                    '\u00a0': ' '
                }
                
                for unicode_char, replacement in replacements.items():
                    markdown_content = markdown_content.replace(unicode_char, replacement)
                
                # Final cleanup - remove any remaining non-ASCII characters
                try:
                    # Test if content can be encoded to CP1252 (Windows console)
                    markdown_content.encode('cp1252')
                    return markdown_content
                except UnicodeEncodeError:
                    # If encoding fails, strip non-ASCII characters
                    cleaned_content = ''.join(char if ord(char) < 128 else ' ' for char in markdown_content)
                    return cleaned_content
                    
        except Exception as e:
            logger.error(f"Failed to get markdown content from {url}: {e}")
            return ""
    
    def _extract_offers_with_ai(self, markdown_content: str, restaurant_name: str) -> List[Dict]:
        """Extract offers using g4f AI model"""
        try:
            prompt = f"""
            You are a helpful assistant that extracts offers data from a menu.

            Extract the following data for each offer:
            - offer_name: The name of the offer
            - offer_description: A detailed description of what's included
            - offer_price: The price in Icelandic krónur (kr) - format as "kr XXXX" where XXXX is the number
            - offer_link: The menu URL

            Return the data in a JSON array format with these exact field names.
            Only extract actual offers/deals, not regular menu items.
            Make sure to include the price in the format "kr XXXX" for each offer.

            The menu is from {restaurant_name}:
            {markdown_content}
            """

            # Try primary AI model
            try:
                response = g4f.ChatCompletion.create(
                    model=AI_MODEL,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": markdown_content}
                    ]
                )
            except Exception as primary_error:
                logger.warning(f"Primary AI model ({AI_MODEL}) failed: {primary_error}")
                # Try fallback model
                try:
                    logger.info(f"Trying fallback AI model for {restaurant_name}")
                    response = g4f.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": markdown_content}
                        ]
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback AI model also failed: {fallback_error}")
                    return []

            # Check if response is empty or None
            if not response or not response.strip():
                logger.warning(f"Received empty response from AI model for {restaurant_name}")
                return []
            
            # Clean up the response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Check if cleaned response is empty
            if not cleaned_response:
                logger.warning(f"Response became empty after cleaning for {restaurant_name}")
                return []

            # Parse JSON response
            try:
                offers_data = json.loads(cleaned_response)
            except json.JSONDecodeError as json_error:
                logger.error(f"Failed to parse AI response as JSON for {restaurant_name}: {json_error}")
                logger.debug(f"Raw response: {response}")
                logger.debug(f"Cleaned response: {cleaned_response}")
                return []
            
            # Convert to our standard format
            offers = []
            for offer_data in offers_data:
                raw_price = offer_data.get('offer_price', '')
                extracted_price = self._extract_price_kr(raw_price)
                
                offer = {
                    'offer_name': offer_data.get('offer_name'),
                    'description': offer_data.get('offer_description'),
                    'price_kr': extracted_price,
                    'pickup_delivery': None,
                    'suits_people': None,
                    'available_weekdays': None,
                    'available_hours': None,
                    'availability_text': None
                }
                
                # Debug logging for price extraction
                if raw_price and not extracted_price:
                    logger.debug(f"Failed to extract price from '{raw_price}' for offer '{offer['offer_name']}'")
                
                # Only add if we have at least a name
                if offer['offer_name']:
                    offers.append(offer)
                    self.field_stats['name_extracted'] += 1
                    if offer['description']:
                        self.field_stats['description_extracted'] += 1
                    if offer['price_kr']:
                        self.field_stats['price_extracted'] += 1

            logger.info(f"AI extracted {len(offers)} offers from {restaurant_name}")
            return offers

        except Exception as e:
            logger.error(f"Failed to extract offers with AI: {e}")
            return []
    
    def _extract_price_kr(self, price_text: str) -> int:
        """Extract price in krónur from text"""
        try:
            import re
            
            # Try different patterns for price extraction
            patterns = [
                r'kr\s*([\d,]+)',  # "kr 1234" or "kr 1,234"
                r'([\d,]+)\s*kr',  # "1234 kr" or "1,234 kr"
                r'kr\s*(\d+)',     # "kr 1234" (no commas)
                r'(\d+)\s*kr',     # "1234 kr" (no commas)
                r'kr\s*(\d+(?:,\d+)*)',  # "kr 1,234,567"
            ]
            
            for pattern in patterns:
                price_match = re.search(pattern, price_text, re.IGNORECASE)
                if price_match:
                    price_str = price_match.group(1).replace(',', '')
                    return int(price_str)
            
            # If no pattern matches, try to extract just numbers
            numbers = re.findall(r'\d+', price_text)
            if numbers:
                # Take the largest number as it's likely the price
                return int(max(numbers, key=lambda x: int(x)))
                
        except Exception as e:
            logger.debug(f"Failed to extract price from '{price_text}': {e}")
        
        return None
    
    def scrape_offers(self, url: str) -> List[Dict]:
        """Scrape offers using AI-powered approach"""
        try:
            # Get markdown content
            markdown_content = asyncio.run(self._get_markdown_content(url))
            
            if not markdown_content:
                logger.warning(f"No markdown content retrieved from {url}")
                return []
            
            # Extract restaurant name from URL for better AI prompting
            restaurant_name = self._extract_restaurant_name_from_url(url)
            
            # Extract offers using AI
            offers = self._extract_offers_with_ai(markdown_content, restaurant_name)
            
            self.field_stats['offers_found'] = len(offers)
            self.log_field_stats(f"AI Parser ({restaurant_name})")
            
            return offers
            
        except Exception as e:
            logger.error(f"Failed to scrape offers with AI: {e}")
            return []
    
    def _extract_restaurant_name_from_url(self, url: str) -> str:
        """Extract restaurant name from URL for better AI prompting"""
        if 'kfc.is' in url:
            return 'KFC Iceland'
        elif 'dominos.is' in url:
            return "Domino's Pizza Iceland"
        elif 'subway.is' in url:
            return 'Subway Iceland'
        else:
            return 'Restaurant' 