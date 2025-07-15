# AI Parser Integration

This document describes the new AI-powered parser that has been integrated into the fastfood scraper.

## Overview

The AI parser uses a two-step approach:
1. **crawl4ai**: Extracts markdown content from restaurant websites
2. **g4f**: Uses AI to extract structured offer data from the markdown

## Features

- **Automatic offer extraction**: AI identifies and extracts offers from menu content
- **Structured data**: Returns offers in the same format as traditional parsers
- **Configurable**: Easy to switch between AI and traditional parsers
- **Fallback support**: Can fall back to traditional parsers if needed

## Configuration

### Parser Selection

In `src/config.py`, you can configure which restaurants use AI vs traditional parsers:

```python
PARSER_CONFIG = {
    'KFC Iceland': 'ai',  # Use AI parser
    "Domino's Pizza Iceland": 'traditional',  # Use traditional parser
    'Subway Iceland': 'traditional',  # Use traditional parser
}
```

### AI Model

You can configure which AI model to use:

```python
AI_MODEL = "gpt-4o-mini"  # Model to use for offer extraction
```

## Usage

### Running with AI Parser

The scraper will automatically use AI parsers for restaurants configured with `'ai'`:

```bash
python run_scraper.py
```

### Testing the AI Parser

Test the AI parser specifically:

```bash
python test_ai_parser.py
```

### Switching Parser Types

Use the utility script to switch between parser types:

```bash
# Show current configuration
python switch_parser.py show

# Switch KFC to use AI parser
python switch_parser.py switch 'KFC Iceland' ai

# Switch KFC back to traditional parser
python switch_parser.py switch 'KFC Iceland' traditional
```

## How It Works

1. **Content Extraction**: Uses `crawl4ai` to get clean markdown from restaurant websites
2. **AI Processing**: Sends markdown to AI model with specific prompts to extract offers
3. **Data Structuring**: Converts AI response to standard offer format
4. **Database Storage**: Saves offers using existing database infrastructure

## Benefits

- **More robust**: AI can handle website changes better than hardcoded selectors
- **Language support**: Works with Icelandic content naturally
- **Flexible**: Can extract offers even when website structure changes
- **Maintainable**: Less need to update selectors when websites change

## Dependencies

The AI parser requires these additional dependencies:
- `crawl4ai==0.7.0`
- `g4f` (already included)

## Troubleshooting

### Common Issues

1. **No offers extracted**: Check if the website is accessible and the AI model is working
2. **Poor quality extraction**: Try adjusting the prompt in `ai_parser.py`
3. **Rate limiting**: The AI service may have rate limits

### Debugging

Enable debug logging to see what the AI parser is doing:

```python
# In config.py
LOG_LEVEL = "DEBUG"
```

## Future Improvements

- Add support for more AI models
- Implement caching for markdown content
- Add retry logic for failed AI requests
- Create more sophisticated prompts for better extraction 