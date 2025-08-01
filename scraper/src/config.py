import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration removed - now using JSON output only

# Parser configuration - which restaurants should use AI parser vs traditional parsers
PARSER_CONFIG = {
    'KFC Iceland': 'traditional',  # Use traditional parser temporarily due to encoding issues
    "Domino's Pizza Iceland": 'traditional',  # Use traditional parser
    'Subway Iceland': 'traditional',  # Use traditional parser
    'Búllan': 'bullan',  # Use custom Búllan parser for accurate div#tilbod parsing
    # All other restaurants will use AI parser by default
}

# AI Model configuration
AI_MODEL = "gpt-4o-mini"  # Model to use for offer extraction
AI_MODEL_FALLBACK = "gemini-2.0-flash"

# Crawling configuration
CRAWL_DELAY = 2  # Delay between restaurant scrapes in seconds

# Logging configuration
LOG_LEVEL = "DEBUG"

def setup_logging():
    """Configure logging to write to both console and file"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "scraper.log"),
            logging.StreamHandler()
        ]
    )
    
    # Set up specific loggers
    logger = logging.getLogger(__name__)
    return logger

# Initialize logging when module is imported
setup_logging() 