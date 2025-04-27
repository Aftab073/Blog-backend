#!/usr/bin/env python

import os
import sys
import django
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogapp_api.settings')
django.setup()

# Now we can import Django models and utilities
from django.db import connection
from django.core.management import call_command
from django.db.utils import OperationalError, ProgrammingError

def initialize_database():
    """Initialize the database by running migrations and creating tables manually if needed"""
    try:
        # First try running migrations the normal way
        logger.info("Running makemigrations...")
        call_command('makemigrations', 'blogapp')
        
        logger.info("Running migrate...")
        call_command('migrate')
        
        # Test if tables exist
        from blogapp.models import Post
        try:
            Post.objects.count()
            logger.info("Database tables created successfully!")
            return True
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Tables not created by standard migration: {e}")
            
            # If tables don't exist, try creating them directly
            logger.info("Attempting to create tables directly...")
            create_tables_manually()
            return True
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

def create_tables_manually():
    """Create database tables manually using SQL"""
    try:
        with connection.cursor() as cursor:
            # Create Post table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS blogapp_post (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                slug VARCHAR(200) UNIQUE NOT NULL,
                excerpt TEXT NOT NULL,
                content TEXT NOT NULL,
                cover_image VARCHAR(100) NULL,
                tags TEXT NOT NULL,
                published_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                author_id INTEGER NOT NULL REFERENCES auth_user(id)
            )
            """)
            
            # Create Contact table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS blogapp_contact (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(254) NOT NULL,
                subject VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME NOT NULL
            )
            """)
            
            logger.info("Tables created manually")
    except Exception as e:
        logger.error(f"Error creating tables manually: {e}")
        raise

if __name__ == "__main__":
    logger.info("Initializing database...")
    if initialize_database():
        logger.info("Database initialization successful!")
    else:
        logger.error("Database initialization failed!")
        sys.exit(1)
