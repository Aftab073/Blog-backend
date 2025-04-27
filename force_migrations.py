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

# Import Django management commands
from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError

def main():
    """Force create migrations and apply them"""
    try:
        # Check database connection
        logger.info("Checking database connection...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            logger.info("Database connection successful!")
        
        # Create migrations for the blogapp app
        logger.info("Creating migrations for blogapp...")
        call_command('makemigrations', 'blogapp', interactive=False)
        
        # Apply migrations
        logger.info("Applying migrations...")
        call_command('migrate', interactive=False)
        
        # Verify tables exist
        logger.info("Verifying tables...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()
            logger.info(f"Found tables: {[t[0] for t in tables]}")
            
            # Check specifically for blogapp_post
            if 'blogapp_post' in [t[0] for t in tables]:
                logger.info("blogapp_post table exists!")
            else:
                logger.warning("blogapp_post table not found, creating it manually...")
                create_tables_manually()
        
        logger.info("Migration process completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error during migration process: {e}")
        return False

def create_tables_manually():
    """Create tables manually if migrations fail"""
    try:
        with connection.cursor() as cursor:
            # Create Post table
            logger.info("Creating blogapp_post table manually...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS blogapp_post (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                slug VARCHAR(200) UNIQUE NOT NULL,
                excerpt TEXT NOT NULL,
                content TEXT NOT NULL,
                cover_image VARCHAR(100) NULL,
                tags JSONB NOT NULL DEFAULT '[]',
                published_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                author_id INTEGER NOT NULL
            )
            """)
            
            # Create Contact table
            logger.info("Creating blogapp_contact table manually...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS blogapp_contact (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(254) NOT NULL,
                subject VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            logger.info("Tables created manually!")
    except Exception as e:
        logger.error(f"Error creating tables manually: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting forced migration process...")
    if main():
        logger.info("Migration process completed successfully!")
        sys.exit(0)
    else:
        logger.error("Migration process failed!")
        sys.exit(1)
