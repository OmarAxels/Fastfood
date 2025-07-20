import logging
import json
import asyncio
from typing import List, Dict
from .base_parser import BaseParser
import g4f
from crawl4ai import AsyncWebCrawler
from config import AI_MODEL, AI_MODEL_FALLBACK

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
                
                # Replace only problematic Unicode characters, preserving Icelandic letters
                replacements = {
                    '\u2192': '->',      # rightwards arrow
                    '\u2190': '<-',      # leftwards arrow
                    '\u2191': '^',       # upwards arrow
                    '\u2193': 'v',       # downwards arrow
                    '\u2013': '-',       # en dash
                    '\u2014': '--',      # em dash
                    '\u2019': "'",       # right single quotation mark
                    '\u2018': "'",       # left single quotation mark
                    '\u201c': '"',       # left double quotation mark
                    '\u201d': '"',       # right double quotation mark
                    '\u00a0': ' ',       # non-breaking space
                    '\u00ae': '(R)',     # registered sign
                    '\u00a9': '(C)',     # copyright sign
                    '\u2022': '*',       # bullet
                    '\u2026': '...',     # horizontal ellipsis
                    '\u00b0': 'deg',     # degree sign
                    # NOTE: Preserve Icelandic letters: á, é, í, ó, ú, ý, þ, ð, æ, ö
                    # Do NOT replace: \u00e1 (á), \u00e9 (é), \u00ed (í), \u00f3 (ó), 
                    # \u00fa (ú), \u00fd (ý), \u00fe (þ), \u00f0 (ð), \u00e6 (æ), \u00f6 (ö)
                }
                
                for unicode_char, replacement in replacements.items():
                    markdown_content = markdown_content.replace(unicode_char, replacement)
                
                # Final cleanup - preserve Icelandic characters while removing problematic ones
                try:
                    # Test if content can be encoded to CP1252 (Windows console)
                    markdown_content.encode('cp1252')
                    return markdown_content
                except UnicodeEncodeError:
                    # If encoding fails, preserve important characters while removing problematic ones
                    import unicodedata
                    
                    # Define characters to preserve
                    icelandic_chars = 'áéíóúýþðæöÁÉÍÓÚÝÞÐÆÖ'
                    
                    def is_safe_char(char):
                        return (ord(char) < 128 or  # ASCII characters
                                char in icelandic_chars or  # Icelandic letters
                                char in 'àèìòùñçüÀÈÌÒÙÑÇÜ')  # Common European letters
                    
                    # Normalize unicode characters first, then filter
                    normalized = unicodedata.normalize('NFKD', markdown_content)
                    cleaned_content = ''.join(char if is_safe_char(char) else ' ' for char in normalized)
                    return cleaned_content
                    
        except UnicodeEncodeError as unicode_error:
            logger.warning(f"Unicode encoding issue for {url}, retrying with simplified approach: {unicode_error}")
            # Try a simplified approach without crawl4ai for problematic sites
            return self._get_simplified_content(url)
        except Exception as e:
            logger.error(f"Failed to get markdown content from {url}: {e}")
            return ""
    
    def _get_simplified_content(self, url: str) -> str:
        """Simplified content extraction using requests as fallback"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Simple HTTP request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text_content = soup.get_text()
            
            # Clean up text - remove excessive whitespace
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Clean only problematic Unicode characters while preserving Icelandic letters
            # Define Icelandic characters to preserve
            icelandic_chars = 'áéíóúýþðæöÁÉÍÓÚÝÞÐÆÖ'
            
            # Create a cleaned version that preserves ASCII and Icelandic characters
            def is_safe_char(char):
                return (ord(char) < 128 or  # ASCII characters
                        char in icelandic_chars or  # Icelandic letters
                        char in 'àèìòùñçüÀÈÌÒÙÑÇÜ')  # Common European letters
            
            clean_text = ''.join(char if is_safe_char(char) else ' ' for char in clean_text)
            
            return clean_text
            
        except Exception as e:
            logger.error(f"Simplified content extraction failed for {url}: {e}")
            return ""
    
    def _extract_offers_with_ai(self, markdown_content: str, restaurant_name: str, url: str = "") -> List[Dict]:
        """Extract offers using g4f AI model"""
        try:
            prompt = f"""
            TASK: Extract ONLY the main promotional combo offers from the "Tilboð" section.

            INSTRUCTIONS:
            1. Look ONLY in the "Tilboð" section at the top of the menu
            3. IGNORE individual burgers, sides, or drinks from other sections
            4. PRESERVE Icelandic characters: á, é, í, ó, ú, ý, þ, ð, æ, ö
            6. Each offer must have name, description, and price

            CRITICAL: Return ONLY valid JSON array, no markdown, no explanations, no formatting.

            [
              {{
                "offer_name": "exact name with Icelandic letters",
                "offer_description": "complete description with Icelandic letters", 
                "offer_price": "kr XXXX",
                "offer_link": "{url}"
              }}
            ]

            MENU DATA:
            {markdown_content[:3000]}...
            """
            
            # Debug: Log the content being sent to AI
            logger.info(f"=== DEBUGGING AI CONTENT FOR {restaurant_name} ===")
            logger.info(f"Total content length: {len(markdown_content)} characters")
            logger.info(f"Content preview (first 2000 chars):\n{markdown_content[:2000]}")
            logger.info(f"Content continuation (chars 2000-4000):\n{markdown_content[2000:4000]}")
            logger.info(f"Content truncated at 3000 chars for AI processing: {len(markdown_content[:3000])} chars")
            logger.info("=== END DEBUGGING CONTENT ===")
            
            # Additional debug: Log the exact content being sent to AI
            ai_content = markdown_content[:3000]
            logger.info(f"=== EXACT AI INPUT CONTENT ===\n{ai_content}\n=== END AI INPUT ===")

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
                        model=AI_MODEL_FALLBACK,
                        messages=[
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": markdown_content}
                        ]
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback AI model also failed: {fallback_error}")
                    return []

            # Debug: Log the AI response
            logger.info(f"=== AI RESPONSE FOR {restaurant_name} ===")
            logger.info(f"Raw AI response: {repr(response)}")
            logger.info("=== END AI RESPONSE ===")
            
            # Check if response is empty or None
            if not response or not response.strip():
                logger.warning(f"Received empty response from AI model for {restaurant_name}")
                logger.debug(f"Content length sent to AI: {len(markdown_content)} characters")
                logger.debug(f"Content preview: {markdown_content[:500]}...")
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
                logger.debug(f"Raw response: {repr(response)}")
                logger.debug(f"Cleaned response: {repr(cleaned_response)}")
                logger.debug(f"Content length sent to AI: {len(markdown_content)} characters")
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

            logger.info(f"=== FINAL EXTRACTED OFFERS FOR {restaurant_name} ===")
            logger.info(f"Total offers extracted: {len(offers)}")
            for i, offer in enumerate(offers, 1):
                logger.info(f"Offer {i}: {offer['offer_name']} - {offer['price_kr']} kr")
                logger.info(f"  Description: {offer['description']}")
            logger.info("=== END EXTRACTED OFFERS ===")
            
            return offers

        except Exception as e:
            logger.error(f"Failed to extract offers with AI: {e}")
            return []
    
    def _extract_price_kr(self, price_text: str) -> int:
        """Extract price in krónur from text"""
        try:
            import re
            
            if not price_text:
                return None
            
            # Clean the input text
            price_text = str(price_text).strip()
            
            # Try different patterns for price extraction (European decimal format)
            patterns = [
                r'kr\s*([\d.]+)',  # "kr 1234" or "kr 1.234" (European thousands separator)
                r'([\d.]+)\s*kr',  # "1234 kr" or "1.234 kr"
                r'kr\s*([\d,]+)',  # "kr 1,234" (comma thousands separator)
                r'([\d,]+)\s*kr',  # "1,234 kr" 
                r'kr\s*(\d+)',     # "kr 1234" (no separators)
                r'(\d+)\s*kr',     # "1234 kr" (no separators)
                r'kr\s*(\d+(?:[.,]\d+)*)',  # "kr 1.234.567" or "kr 1,234,567"
                r'(\d{1,2}\.\d{3})',  # European format like "2.990" or "10.900"
                r'(\d{3,5})',      # Any 3-5 digit number (common price range)
            ]
            
            for pattern in patterns:
                price_match = re.search(pattern, price_text, re.IGNORECASE)
                if price_match:
                    price_str = price_match.group(1)
                    
                    # Handle European decimal format (period as thousands separator)
                    if '.' in price_str:
                        if len(price_str.split('.')[-1]) == 3:
                            # Likely thousands separator (e.g., "2.190" = 2190)
                            price_str = price_str.replace('.', '')
                        elif len(price_str.split('.')[-1]) == 2:
                            # Likely decimal (e.g., "10.90" = 1090 kr)
                            price_str = price_str.replace('.', '') + '0'
                    else:
                        # Regular comma thousands separator
                        price_str = price_str.replace(',', '')
                    
                    try:
                        price_int = int(price_str)
                        
                        # Validate price range (reasonable for Icelandic restaurant offers)
                        if 500 <= price_int <= 15000:
                            return price_int
                    except ValueError:
                        continue
            
            # If no pattern matches, try to extract just numbers in reasonable range
            numbers = re.findall(r'\d+', price_text)
            if numbers:
                for num_str in numbers:
                    num = int(num_str)
                    if 500 <= num <= 15000:  # Reasonable price range
                        return num
                        
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
            offers = self._extract_offers_with_ai(markdown_content, restaurant_name, url)
            
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
        elif 'tommis.is' in url:
            return 'Búllan (Hamborgarabúllan)'
        else:
            return 'Restaurant' 