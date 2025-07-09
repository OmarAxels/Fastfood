import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import DATABASE_URL

logger = logging.getLogger(__name__)

Base = declarative_base()


class Restaurant(Base):
    """Database model for restaurants"""
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    website = Column(String(500))
    menu_page = Column(String(500))
    offers_page = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to offers
    offers = relationship("Offer", back_populates="restaurant")
    
    def __repr__(self):
        return f"<Restaurant(name='{self.name}', website='{self.website}')>"


class Offer(Base):
    """Database model for fastfood offers"""
    __tablename__ = 'offers'
    
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    offer_name = Column(String(500), nullable=False)
    description = Column(Text)
    price_kr = Column(Float)  # Price in Icelandic krónur
    pickup_delivery = Column(String(100))  # sækja/sótt information
    suits_people = Column(Integer)  # Number of people it suits
    
    # NEW: Temporal availability fields
    available_weekdays = Column(String(200))  # Comma-separated Icelandic weekdays (e.g., "mánudagur,þriðjudagur")
    available_hours = Column(String(200))     # Time ranges (e.g., "11:00-15:00,17:00-21:00")
    availability_text = Column(Text)          # Raw text containing temporal info for reference
    
    scraped_at = Column(DateTime, default=datetime.utcnow)
    source_url = Column(String(500))
    
    # Relationship to restaurant
    restaurant = relationship("Restaurant", back_populates="offers")
    
    def __repr__(self):
        return f"<Offer(restaurant_id={self.restaurant_id}, name='{self.offer_name}', price={self.price_kr})>"


class DatabaseManager:
    """Handles database connections and operations"""
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info("Database connection initialized")
    
    def create_tables(self):
        """Create all tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def get_or_create_restaurant(self, restaurant_data):
        """Get existing restaurant or create a new one"""
        session = self.get_session()
        try:
            # Check if restaurant already exists
            restaurant = session.query(Restaurant).filter_by(name=restaurant_data['name']).first()
            
            if not restaurant:
                # Create new restaurant
                restaurant = Restaurant(
                    name=restaurant_data['name'],
                    website=restaurant_data.get('website'),
                    menu_page=restaurant_data.get('menu_page'),
                    offers_page=restaurant_data.get('offers_page')
                )
                session.add(restaurant)
                session.commit()
                logger.info(f"Created new restaurant: {restaurant.name}")
            
            return restaurant
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to get or create restaurant: {e}")
            raise
        finally:
            session.close()
    
    def clear_restaurant_offers(self, restaurant_id):
        """Clear all existing offers for a restaurant"""
        session = self.get_session()
        try:
            # Get restaurant name for logging
            restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
            restaurant_name = restaurant.name if restaurant else "Unknown"
            
            # Delete all existing offers for this restaurant
            deleted_count = session.query(Offer).filter_by(restaurant_id=restaurant_id).delete()
            session.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleared {deleted_count} existing offers for {restaurant_name}")
            
            return deleted_count
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to clear offers for restaurant {restaurant_id}: {e}")
            raise
        finally:
            session.close()
    
    def save_offers_batch(self, offers_data, restaurant_data, clear_existing=True):
        """Save multiple offers for a restaurant, optionally clearing existing ones first"""
        session = self.get_session()
        try:
            # Get or create restaurant
            restaurant = self.get_or_create_restaurant(restaurant_data)
            
            # Clear existing offers if requested
            if clear_existing:
                deleted_count = session.query(Offer).filter_by(restaurant_id=restaurant.id).delete()
                if deleted_count > 0:
                    logger.info(f"Cleared {deleted_count} existing offers for {restaurant.name}")
            
            # Save new offers
            saved_count = 0
            for offer_data in offers_data:
                # Remove restaurant_name if it exists
                offer_data.pop('restaurant_name', None)
                offer_data['restaurant_id'] = restaurant.id
                
                offer = Offer(**offer_data)
                session.add(offer)
                saved_count += 1
            
            session.commit()
            logger.info(f"Saved {saved_count} new offers for {restaurant.name}")
            return saved_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save offers batch: {e}")
            raise
        finally:
            session.close()
    
    def save_offer(self, offer_data, restaurant_data=None):
        """Save an offer to the database"""
        session = self.get_session()
        try:
            # Handle backward compatibility: if offer_data contains restaurant_name
            if 'restaurant_name' in offer_data and restaurant_data is None:
                restaurant_data = {'name': offer_data.pop('restaurant_name')}
            
            # Get or create restaurant
            if restaurant_data:
                restaurant = self.get_or_create_restaurant(restaurant_data)
                offer_data['restaurant_id'] = restaurant.id
            
            # Remove restaurant_name if it still exists in offer_data
            offer_data.pop('restaurant_name', None)
            
            offer = Offer(**offer_data)
            session.add(offer)
            session.commit()
            
            # Get restaurant name for logging
            restaurant_name = session.query(Restaurant).filter_by(id=offer.restaurant_id).first().name
            logger.info(f"Saved offer: {offer.offer_name} from {restaurant_name}")
            return offer
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save offer: {e}")
            raise
        finally:
            session.close()
    
    def get_offers_count(self):
        """Get total count of offers in database"""
        session = self.get_session()
        try:
            count = session.query(Offer).count()
            return count
        finally:
            session.close()
    
    def get_restaurants_count(self):
        """Get total count of restaurants in database"""
        session = self.get_session()
        try:
            count = session.query(Restaurant).count()
            return count
        finally:
            session.close() 