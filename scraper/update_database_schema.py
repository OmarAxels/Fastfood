#!/usr/bin/env python3
"""
Database schema update script to add temporal availability fields
"""

import logging
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from database import DatabaseManager
from config import setup_logging
from sqlalchemy import text

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def update_database_schema():
    """Add new temporal availability columns to the offers table"""
    
    logger.info("Starting database schema update...")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Get a session for manual operations
        session = db_manager.get_session()
        
        try:
            # Check if the new columns already exist (PostgreSQL version)
            result = session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'offers' AND table_schema = 'public'
            """))
            columns = [row[0] for row in result.fetchall()]
            
            
            new_columns = [
                ('available_weekdays', 'VARCHAR(200)'),
                ('available_hours', 'VARCHAR(200)'),
                ('availability_text', 'TEXT')
            ]
            
            for column_name, column_type in new_columns:
                if column_name not in columns:
                    logger.info(f"Adding column '{column_name}' to offers table...")
                    session.execute(text(f"ALTER TABLE offers ADD COLUMN {column_name} {column_type}"))
                    session.commit()
                    logger.info(f"Successfully added column '{column_name}'")
                else:
                    logger.info(f"Column '{column_name}' already exists, skipping...")
            
            logger.info("Database schema update completed successfully!")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update schema: {e}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Database schema update failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_database_schema() 