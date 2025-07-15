#!/usr/bin/env python3
"""
Utility script to switch between AI and traditional parsers
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def switch_parser(restaurant_name: str, parser_type: str):
    """Switch a restaurant to use a different parser type"""
    from config import PARSER_CONFIG
    
    if restaurant_name not in PARSER_CONFIG:
        print(f"Error: Restaurant '{restaurant_name}' not found in configuration")
        return False
    
    if parser_type not in ['ai', 'traditional']:
        print(f"Error: Parser type must be 'ai' or 'traditional', got '{parser_type}'")
        return False
    
    # Update the configuration
    PARSER_CONFIG[restaurant_name] = parser_type
    
    print(f"Switched {restaurant_name} to use {parser_type} parser")
    return True

def show_current_config():
    """Show current parser configuration"""
    from config import PARSER_CONFIG
    
    print("Current Parser Configuration:")
    print("=" * 40)
    for restaurant, parser_type in PARSER_CONFIG.items():
        print(f"{restaurant}: {parser_type}")
    print()

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python switch_parser.py show                    # Show current config")
        print("  python switch_parser.py switch <restaurant> <type>  # Switch parser")
        print()
        print("Examples:")
        print("  python switch_parser.py switch 'KFC Iceland' ai")
        print("  python switch_parser.py switch 'KFC Iceland' traditional")
        return
    
    command = sys.argv[1]
    
    if command == "show":
        show_current_config()
    elif command == "switch":
        if len(sys.argv) != 4:
            print("Error: switch command requires restaurant name and parser type")
            return
        
        restaurant_name = sys.argv[2]
        parser_type = sys.argv[3]
        
        if switch_parser(restaurant_name, parser_type):
            show_current_config()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main() 