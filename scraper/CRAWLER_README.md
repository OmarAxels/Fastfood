# Website Crawler for Fast Food Restaurants

This crawler automatically discovers menu and offers pages for restaurants in the `fastfood-info.json` file and downloads offers page HTML.

## Features

- **Automatic Discovery**: Finds menu and offers pages for restaurants that don't have them specified
- **Multi-language Support**: Supports both English and Icelandic terms for better coverage of Icelandic websites
- **HTML Download**: Downloads offers page HTML and saves to `/offers_pages/` folder
- **JSON Update**: Updates the `fastfood-info.json` file with discovered URLs
- **Error Handling**: Graceful handling of network errors and inaccessible websites
- **Respectful Crawling**: Includes delays between requests to avoid overwhelming servers

## Usage

### Run the Full Crawler
```bash
cd scraper
python website_crawler.py
```

This will:
1. Process all restaurants in `fastfood-info.json`
2. Find missing menu and offers pages
3. Update the JSON file with discovered URLs
4. Download offers page HTML to `offers_pages/` folder

### Test Before Full Run
```bash
python test_crawler.py
```

This runs tests on:
- A single restaurant without menu/offers pages (discovery test)
- Existing restaurants with offers pages (HTML download test)

## How It Works

### 1. Pattern Matching
The crawler looks for links containing these patterns:

**Menu Page Patterns:**
- `menu`, `matseðill` (Icelandic)
- `vörur` (products in Icelandic), `panta` (order in Icelandic)
- `food`, `eat`, `order`

**Offers Page Patterns:**
- `tilbod` (offers in Icelandic)
- `offer`, `deal`, `special`, `promotion`, `discount`
- `kampanja` (campaign in Icelandic), `afsláttur` (discount in Icelandic)

### 2. Website Name Extraction
For HTML filenames, the crawler extracts website names by:
- Removing `www.` prefix
- Removing domain extensions (`.is`, `.com`, etc.)
- Example: `https://www.dominos.is` → `dominos.html`

### 3. File Structure
```
scraper/
├── website_crawler.py      # Main crawler script
├── test_crawler.py         # Test script
├── fastfood-info.json      # Restaurant data (updated by crawler)
└── offers_pages/           # Downloaded HTML files
    ├── dominos.html
    ├── kfc.html
    └── ...
```

## Configuration

You can modify the crawler behavior by editing the patterns in `website_crawler.py`:

```python
# Add more menu patterns
self.menu_patterns = [
    r'menu',
    r'your_custom_pattern',
    # ...
]

# Add more offers patterns
self.offers_patterns = [
    r'tilbod',
    r'your_custom_pattern',
    # ...
]
```

## Output

### JSON Updates
The crawler adds `menu_page` and `offers_page` fields to restaurants:

```json
{
  "name": "Restaurant Name",
  "website": "https://example.is",
  "menu_page": "https://example.is/menu",
  "offers_page": "https://example.is/offers"
}
```

### HTML Downloads
Offers page HTML is saved as `{website_name}.html` in the `offers_pages/` folder.

## Error Handling

The crawler handles:
- Network timeouts and connection errors
- Invalid URLs
- Websites that don't respond
- Missing or malformed HTML

Errors are logged to console, and the crawler continues with the next restaurant.

## Dependencies

Required packages (already in `requirements.txt`):
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML parsing

## Examples

### Successful Discovery
```
Crawling Metro (https://www.metro.is)
  Found menu page: https://www.metro.is/matseðill
  Found offers page: https://www.metro.is/tilbod
  Saved offers page HTML: offers_pages/metro.html
```

### Already Has Pages
```
Crawling Domino's Pizza Iceland (https://www.dominos.is)
  Already has menu and offers pages
  Saved offers page HTML: offers_pages/dominos.html
```

### Error Handling
```
Crawling Some Restaurant (https://broken-site.is)
Error fetching https://broken-site.is: Connection timeout
``` 