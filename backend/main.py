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
            "/health": "Health check"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

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