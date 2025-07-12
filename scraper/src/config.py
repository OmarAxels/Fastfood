import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Validate required environment variables
missing_vars = [
    var for var, value in [
        ("user", USER),
        ("password", PASSWORD),
        ("host", HOST),
        ("port", PORT),
        ("dbname", DBNAME)
    ] if not value
]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Logging configuration
def setup_logging():
    """Configure logging to write to both console and file"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
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