#!/usr/bin/env python3
"""
Website Crawler for Fast Food Restaurants
Crawls restaurant websites to find menu and offers pages,
updates the JSON file, and downloads offers page HTML.
"""

import json
import os
import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class WebsiteCrawler:
    def __init__(self, json_file_path: str = "fastfood-info.json", offers_folder: str = "offers_pages"):
        self.json_file_path = json_file_path
        self.offers_folder = offers_folder
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create offers folder if it doesn't exist
        os.makedirs(self.offers_folder, exist_ok=True)
        
        # Common patterns for menu and offers pages
        self.menu_patterns = [
            r'menu',
            r'matseðill',  # Icelandic for menu
            r'vörur',      # Icelandic for products
            r'panta',      # Icelandic for order
            r'food',
            r'eat',
            r'order'
        ]
        
        self.offers_patterns = [
            r'tilbod',     # Icelandic for offers
            r'offer',
            r'deal',
            r'special',
            r'promotion',
            r'discount',
            r'kampanja',   # Icelandic for campaign
            r'afsláttur'   # Icelandic for discount
        ]

    def load_restaurants(self) -> List[Dict]:
        """Load restaurant data from JSON file."""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.json_file_path} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return []

    def save_restaurants(self, restaurants: List[Dict]) -> None:
        """Save updated restaurant data to JSON file."""
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(restaurants, f, indent=2, ensure_ascii=False)
            print(f"Updated {self.json_file_path}")
        except Exception as e:
            print(f"Error saving JSON: {e}")

    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse webpage content."""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_website_name(self, url: str) -> str:
        """Extract website name from URL for filename."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix and .is/.com suffix
        domain = re.sub(r'^www\.', '', domain)
        domain = re.sub(r'\.(is|com|net|org)$', '', domain)
        return domain

    def find_links_by_patterns(self, soup: BeautifulSoup, base_url: str, patterns: List[str]) -> List[str]:
        """Find links that match given patterns."""
        found_links = []
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href'].lower()
            text = link.get_text().lower().strip()
            
            # Check if href or link text matches any pattern
            for pattern in patterns:
                if re.search(pattern, href) or re.search(pattern, text):
                    full_url = urljoin(base_url, link['href'])
                    if full_url not in found_links:
                        found_links.append(full_url)
                        break
        
        return found_links

    def find_menu_and_offers_pages(self, website_url: str) -> Tuple[Optional[str], Optional[str]]:
        """Find menu and offers pages for a given website."""
        soup = self.get_page_content(website_url)
        if not soup:
            return None, None
        
        # Find menu page candidates
        menu_links = self.find_links_by_patterns(soup, website_url, self.menu_patterns)
        
        # Find offers page candidates
        offers_links = self.find_links_by_patterns(soup, website_url, self.offers_patterns)
        
        # Select best candidates (prefer shorter, more direct paths)
        menu_page = None
        if menu_links:
            menu_page = min(menu_links, key=len)
        
        offers_page = None
        if offers_links:
            offers_page = min(offers_links, key=len)
        
        return menu_page, offers_page

    def download_offers_page(self, offers_url: str, website_name: str) -> None:
        """Download offers page HTML and save to file."""
        try:
            response = self.session.get(offers_url, timeout=10)
            response.raise_for_status()
            
            filename = f"{website_name}.html"
            filepath = os.path.join(self.offers_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"Saved offers page HTML: {filepath}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading offers page {offers_url}: {e}")
        except Exception as e:
            print(f"Error saving offers HTML: {e}")

    def crawl_restaurant(self, restaurant: Dict) -> Tuple[Dict, str]:
        """Crawl a single restaurant's website. Returns (updated_restaurant, status)."""
        name = restaurant.get('name', 'Unknown')
        website = restaurant.get('website')
        if not website:
            print(f"No website found for {name}")
            return restaurant, 'no_website'
        print(f"\nCrawling {name} ({website})")
        # Always try to find menu/offers pages, even if they exist
        menu_page, offers_page = self.find_menu_and_offers_pages(website)
        updated_restaurant = restaurant.copy()
        updated = False
        if menu_page and menu_page != restaurant.get('menu_page'):
            updated_restaurant['menu_page'] = menu_page
            print(f"  Found menu page: {menu_page}")
            updated = True
        if offers_page and offers_page != restaurant.get('offers_page'):
            updated_restaurant['offers_page'] = offers_page
            print(f"  Found offers page: {offers_page}")
            updated = True
        # Download offers page HTML if found
        if offers_page:
            website_name = self.extract_website_name(website)
            self.download_offers_page(offers_page, website_name)
        # Status logic
        if not menu_page and not offers_page:
            return updated_restaurant, 'no_menu_or_offers'
        elif not offers_page:
            return updated_restaurant, 'no_offers'
        elif not menu_page:
            return updated_restaurant, 'no_menu'
        elif updated:
            return updated_restaurant, 'updated'
        else:
            return updated_restaurant, 'unchanged'

    def crawl_all(self) -> None:
        """Crawl all restaurants in the JSON file."""
        restaurants = self.load_restaurants()
        if not restaurants:
            return
        print(f"Found {len(restaurants)} restaurants to process")
        updated_restaurants = []
        summary = {'updated': [], 'unchanged': [], 'no_website': [], 'no_menu_or_offers': [], 'no_menu': [], 'no_offers': []}
        for i, restaurant in enumerate(restaurants, 1):
            print(f"\n[{i}/{len(restaurants)}] Processing restaurant...")
            updated_restaurant, status = self.crawl_restaurant(restaurant)
            updated_restaurants.append(updated_restaurant)
            summary.setdefault(status, []).append(updated_restaurant.get('name', 'Unknown'))
            time.sleep(1)
        self.save_restaurants(updated_restaurants)
        print(f"\nCrawling completed! Results saved to {self.json_file_path}")
        print("\nSummary:")
        for k, v in summary.items():
            print(f"  {k}: {len(v)} - {v}")


def main():
    """Main function to run the crawler."""
    crawler = WebsiteCrawler()
    crawler.crawl_all()


if __name__ == "__main__":
    main() 