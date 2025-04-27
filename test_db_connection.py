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

# Now we can import Django models
from django.db import connection, DatabaseError
from django.conf import settings
from blogapp.models import Post, Contact

def test_database_connection():
    """Test the database connection and check if tables exist"""
    try:
        # Print database settings
        logger.info(f"Database engine: {settings.DATABASES['default']['ENGINE']}")
        if 'NAME' in settings.DATABASES['default']:
            logger.info(f"Database name: {settings.DATABASES['default']['NAME']}")
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            logger.info(f"Database connection test: {result}")
        
        # Check if tables exist
        try:
            post_count = Post.objects.count()
            logger.info(f"Post table exists. Post count: {post_count}")
        except DatabaseError as e:
            logger.error(f"Error accessing Post table: {e}")
        
        try:
            contact_count = Contact.objects.count()
            logger.info(f"Contact table exists. Contact count: {contact_count}")
        except DatabaseError as e:
            logger.error(f"Error accessing Contact table: {e}")
            
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False
    
    return True

def list_all_tables():
    """List all tables in the database"""
    try:
        with connection.cursor() as cursor:
            if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            else:  # PostgreSQL
                cursor.execute("""SELECT table_name FROM information_schema.tables 
                               WHERE table_schema = 'public'""")
            tables = cursor.fetchall()
            logger.info("Database tables:")
            for table in tables:
                logger.info(f"  - {table[0]}")
    except Exception as e:
        logger.error(f"Error listing tables: {e}")

if __name__ == "__main__":
    logger.info("Testing database connection...")
    if test_database_connection():
        logger.info("Database connection successful!")
        list_all_tables()
    else:
        logger.error("Database connection failed!")
        sys.exit(1)
