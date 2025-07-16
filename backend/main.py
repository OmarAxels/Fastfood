from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
from dotenv import load_dotenv
import json
from pathlib import Path
import logging
import subprocess
import sys

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


# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models (matching the scraper's schema)
class Restaurant(Base):
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    website = Column(String(500))
    menu_page = Column(String(500))
    offers_page = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    offers = relationship("Offer", back_populates="restaurant")

class Offer(Base):
    __tablename__ = 'offers'
    
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    offer_name = Column(String(500), nullable=False)
    description = Column(Text)
    price_kr = Column(Float)
    pickup_delivery = Column(String(100))
    suits_people = Column(Integer)
    
    # Temporal availability fields
    available_weekdays = Column(String(200))
    available_hours = Column(String(200))
    availability_text = Column(Text)
    
    scraped_at = Column(DateTime, default=datetime.utcnow)
    source_url = Column(String(500))
    
    restaurant = relationship("Restaurant", back_populates="offers")

# Pydantic Models (API responses)
class OfferResponse(BaseModel):
    id: int
    name: str
    
    @classmethod
    def from_orm_offer(cls, offer):
        return cls(
            id=offer.id,
            name=offer.offer_name,
            description=offer.description,
            price_kr=offer.price_kr,
            available_weekdays=offer.available_weekdays,
            available_hours=offer.available_hours,
            availability_text=offer.availability_text,
            pickup_delivery=offer.pickup_delivery,
            suits_people=offer.suits_people,
            scraped_at=offer.scraped_at,
            source_url=offer.source_url
        )
    description: Optional[str] = None
    price_kr: Optional[float] = None
    available_weekdays: Optional[str] = None
    available_hours: Optional[str] = None
    availability_text: Optional[str] = None
    pickup_delivery: Optional[str] = None
    suits_people: Optional[int] = None
    scraped_at: Optional[datetime] = None
    source_url: Optional[str] = None

    class Config:
        from_attributes = True

class RestaurantResponse(BaseModel):
    id: int
    name: str
    website: Optional[str] = None
    menu_page: Optional[str] = None
    offers_page: Optional[str] = None
    created_at: Optional[datetime] = None
    offers: List[OfferResponse] = []

    class Config:
        from_attributes = True

class RestaurantsListResponse(BaseModel):
    restaurants: List[RestaurantResponse]
    total_offers: int
    last_updated: Optional[datetime] = None

# Add request model for LLM extractor
class LLMExtractorRequest(BaseModel):
    offer_name: str
    description: str

# FastAPI app
app = FastAPI(
    title="Fastfood Offers API",
    description="API to access fastfood offers from Icelandic restaurants",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/", response_model=dict)
def read_root():
    return {
        "message": "Fastfood Offers API",
        "version": "1.0.0",
        "endpoints": {
            "/restaurants": "Get all restaurants with their offers",
            "/restaurants/{restaurant_id}": "Get specific restaurant with offers",
            "/enhanced-offers": "Get restaurants with enhanced food visualization data",
            "/health": "Health check"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/test/llm_food_extractor")
async def test_llm_food_extractor(request: LLMExtractorRequest):
    """
    Test the LLM food extractor script.
    Accepts POST requests with offer_name and description.
    Calls the Python LLM extractor script and returns the result.
    """
    try:
        # Locate the scraper directory and CLI script
        scraper_dir = Path("../scraper")
        if not scraper_dir.exists():
            raise HTTPException(status_code=500, detail="Scraper directory not found")
        
        script_path = scraper_dir / "src" / "llm_food_extractor_cli.py"
        if not script_path.exists():
            raise HTTPException(status_code=500, detail=f"LLM extractor CLI script not found at {script_path}")
        
        # Prepare the offer data as JSON
        offer_data = [{
            "offer_name": request.offer_name,
            "description": request.description,
            "price_kr": None,
            "pickup_delivery": None,
            "suits_people": None,
            "available_weekdays": None,
            "available_hours": None,
            "restaurant_name": "Test"
        }]
        
        # Run the subprocess with proper working directory
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps(offer_data),
            capture_output=True,
            text=True,
            cwd=str(scraper_dir),  # Set working directory to scraper
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or "Unknown error"
            raise HTTPException(
                status_code=500,
                detail=f"LLM extractor failed: {error_msg}"
            )
        
        # Parse the JSON response
        try:
            # Extract JSON from output (ignore debug prints)
            output_lines = result.stdout.strip()
            
            # Find the JSON part (starts with [ or {)
            json_start = -1
            for i, char in enumerate(output_lines):
                if char in '[{':
                    json_start = i
                    break
            
            if json_start == -1:
                raise ValueError("No JSON found in output")
            
            json_part = output_lines[json_start:]
            output_data = json.loads(json_part)
            return output_data[0] if output_data else {}
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse extractor output: {e}. Output: {result.stdout}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"No valid JSON found in output: {e}. Output: {result.stdout}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"LLM extractor execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM extractor execution failed: {str(e)}")

@app.get("/enhanced-offers")
def get_enhanced_offers(db: Session = Depends(get_db)):
    """Get restaurants with enhanced food information including food items, meal types, etc."""
    try:
        # Try to read the enhanced offers JSON file from the scraper
        
        # Look for the enhanced offers file in likely locations
        possible_paths = [
            "../scraper/enhanced_offers_with_food_info.json",
            "enhanced_offers_with_food_info.json",
            "../enhanced_offers_with_food_info.json"
        ]
        
        enhanced_data = None
        for path in possible_paths:
            file_path = Path(path)
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    enhanced_data = json.load(f)
                break
        
        if not enhanced_data:
            # Fallback to basic data if enhanced file not found
            return get_restaurants(db)
        
        def get_restaurant_logo(restaurant_name: str) -> str | None:
            """Get logo URL for restaurant"""
            name = restaurant_name.lower()
            if 'dominos' in name or 'domino' in name:
                return '/dominos.png'
            elif 'kfc' in name:
                return '/kfc.png'
            elif 'subway' in name:
                return '/subway.jpg'
            elif 'hlöllabátar' in name or 'hlollabatar' in name:
                return '/hlolli.png'
            elif 'búllan' in name or 'bullan' in name:
                return '/bullan.svg'
            elif 'noodle station' in name or 'noodlestation' in name:
                return '/noodlestation.png'
            return None
        
        def get_restaurant_background_color(restaurant_name: str) -> str:
            """Get background color for restaurant"""
            name = restaurant_name.lower()
            if 'dominos' in name or 'domino' in name:
                return '#4133FF'  # Blue
            elif 'kfc' in name:
                return '#FF0000'  # Red
            elif 'subway' in name:
                return '#4ED512'  # Green
            elif 'hlöllabátar' in name or 'hlollabatar' in name:
                return '#DC291A'  # Red (from HlöllaBátar logo)
            elif 'búllan' in name or 'bullan' in name:
                return '#DC291A'  # Red (from Bullan logo)
            elif 'noodle station' in name or 'noodlestation' in name:
                return '#FF6B35'  # Orange (typical for noodle restaurants)
            return '#FFFFFF'  # White
        
        # Group enhanced offers by restaurant
        restaurant_map = {}
        
        for enhanced_offer in enhanced_data.get('offers', []):
            restaurant_name = enhanced_offer.get('restaurant_name', 'Unknown')
            
            if restaurant_name not in restaurant_map:
                restaurant_map[restaurant_name] = {
                    "id": len(restaurant_map) + 1,
                    "name": restaurant_name,
                    "website": None,
                    "logo": get_restaurant_logo(restaurant_name),
                    "background_color": get_restaurant_background_color(restaurant_name),
                    "offers": []
                }
            
            # Convert enhanced offer to match frontend expectations
            offer = {
                "id": len(restaurant_map[restaurant_name]["offers"]) + 1,
                "name": enhanced_offer.get('offer_name', 'Unknown Offer'),
                "description": enhanced_offer.get('description', ''),
                "price_kr": enhanced_offer.get('price_kr'),
                "available_weekdays": enhanced_offer.get('available_weekdays'),
                "available_hours": enhanced_offer.get('available_hours'),
                "availability_text": enhanced_offer.get('availability_text'),
                "pickup_delivery": enhanced_offer.get('pickup_delivery'),
                "suits_people": enhanced_offer.get('suits_people'),
                "scraped_at": enhanced_offer.get('scraped_at'),
                "source_url": enhanced_offer.get('source_url'),
                
                # Enhanced food information
                "food_items": enhanced_offer.get('food_items', []),
                "meal_type": enhanced_offer.get('meal_type'),
                "is_combo": enhanced_offer.get('is_combo', False),
                "complexity_score": enhanced_offer.get('complexity_score'),
                "total_food_items": enhanced_offer.get('total_food_items', 0),
                "main_items": enhanced_offer.get('main_items', []),
                "side_items": enhanced_offer.get('side_items', []),
                "drink_items": enhanced_offer.get('drink_items', []),
                "dessert_items": enhanced_offer.get('dessert_items', []),
                "visual_summary": enhanced_offer.get('visual_summary', '')
            }
            
            restaurant_map[restaurant_name]["offers"].append(offer)
        
        # Convert to list and calculate totals
        restaurants = list(restaurant_map.values())
        total_offers = sum(len(r["offers"]) for r in restaurants)
        last_updated = enhanced_data.get('scraped_at', datetime.utcnow().isoformat())
        
        return {
            "restaurants": restaurants,
            "total_offers": total_offers,
            "last_updated": last_updated
        }
        
    except Exception as e:
        logging.error(f"Failed to load enhanced offers: {e}")
        # Fallback to basic data
        return get_restaurants(db)

@app.get("/restaurants", response_model=RestaurantsListResponse)
def get_restaurants(db: Session = Depends(get_db)):
    """Get all restaurants with their offers"""
    try:
        restaurants_db = db.query(Restaurant).all()
        
        # Convert to response format
        restaurants_response = []
        total_offers = 0
        last_updated = None
        
        for restaurant_db in restaurants_db:
            # Convert offers
            offers_response = [OfferResponse.from_orm_offer(offer) for offer in restaurant_db.offers]
            total_offers += len(offers_response)
            
            # Find last update
            for offer in restaurant_db.offers:
                if offer.scraped_at and (not last_updated or offer.scraped_at > last_updated):
                    last_updated = offer.scraped_at
            
            # Create restaurant response
            restaurant_response = RestaurantResponse(
                id=restaurant_db.id,
                name=restaurant_db.name,
                website=restaurant_db.website,
                menu_page=restaurant_db.menu_page,
                offers_page=restaurant_db.offers_page,
                created_at=restaurant_db.created_at,
                offers=offers_response
            )
            restaurants_response.append(restaurant_response)
        
        return RestaurantsListResponse(
            restaurants=restaurants_response,
            total_offers=total_offers,
            last_updated=last_updated
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """Get specific restaurant with its offers"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return restaurant

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 