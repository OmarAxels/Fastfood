#!/usr/bin/env python3
"""
Copy the enhanced_offers_with_food_info.json to the frontend after scraping
"""
import shutil
import os
from pathlib import Path

def copy_data_to_frontend():
    # Source file from scraper
    source = Path(__file__).parent / "enhanced_offers_with_food_info.json"
    
    # Destination in frontend
    destination = Path(__file__).parent.parent.parent / "reykjavik-food-finder" / "src" / "data" / "enhanced_offers_with_food_info.json"
    
    # Ensure destination directory exists
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy the file
    if source.exists():
        shutil.copy2(source, destination)
        print(f"✅ Copied {source.name} to frontend")
        print(f"   From: {source}")
        print(f"   To: {destination}")
    else:
        print(f"❌ Source file not found: {source}")

if __name__ == "__main__":
    copy_data_to_frontend()