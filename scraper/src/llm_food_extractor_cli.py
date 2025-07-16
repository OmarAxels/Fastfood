#!/usr/bin/env python3
"""
CLI wrapper for LLM Food Extractor that accepts stdin input
"""
import sys
import json
import os
from pathlib import Path

# Set UTF-8 encoding for stdout to handle Icelandic characters
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from llm_food_extractor import LLMFoodExtractor

def main():
    try:
        # Change to scraper directory to find food_categories.json
        scraper_dir = Path(__file__).parent.parent
        os.chdir(scraper_dir)
        
        # Read JSON from stdin
        input_data = sys.stdin.read()
        offers = json.loads(input_data)
        
        # Initialize extractor (will look for food_categories.json in current directory)
        extractor = LLMFoodExtractor()
        
        # Process offers
        enhanced_offers = extractor.extract_food_info_batch(offers)
        
        # Output results as JSON with proper encoding
        output = json.dumps(enhanced_offers, ensure_ascii=False, indent=2)
        print(output)
        
    except Exception as e:
        # Output error as JSON to stderr
        error_data = {"error": str(e), "type": type(e).__name__}
        error_output = json.dumps(error_data, ensure_ascii=False)
        print(error_output, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 