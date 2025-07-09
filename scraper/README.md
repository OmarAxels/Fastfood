# Fastfood Scraper - Iceland

A Python web scraper that extracts special offers from Icelandic fastfood websites in Reykjavík.

## Features

- Scrapes offers from KFC Iceland and Domino's Pizza Iceland
- Extracts: offer name, description, price (kr.), pickup/delivery info (sækja/sótt), number of people
- Stores data in database using SQLAlchemy
- Detailed logging with extraction statistics
- Configurable restaurant list via JSON

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   Create a `.env` file with your database URL:
   ```
   DATABASE_URL=postgresql://username:password@localhost/fastfood_db
   # or for SQLite:
   # DATABASE_URL=sqlite:///fastfood.db
   ```

3. **Run the scraper:**
   ```bash
   cd scraper
   source venv/Scripts/activate
   python run_scraper.py
   ```

## Configuration

Edit `fastfood-info-test.json` to add/modify restaurants:

```json
[
  {
    "name": "Restaurant Name",
    "website": "https://example.com",
    "menu_page": "https://example.com/menu",
    "offers_page": "https://example.com/offers"
  }
]
```

## Database Schema

The scraper creates an `offers` table with:
- `id` (Primary key)
- `restaurant_name` (Restaurant name)
- `offer_name` (Name of the offer)
- `description` (Offer description)
- `price_kr` (Price in Icelandic krónur)
- `pickup_delivery` (sækja/sótt information)
- `suits_people` (Number of people it serves)
- `scraped_at` (Timestamp)
- `source_url` (Source page URL)

## Logging

Logs are written to `logs/scraper.log` and include:
- Scraping progress and errors
- Field extraction statistics
- Summary of successful vs failed extractions

## Supported Sites

- KFC Iceland (kfc.is)
- Domino's Pizza Iceland (dominos.is)

New restaurant parsers can be added by extending the `BaseParser` class. 