#!/usr/bin/env python3
"""
RSS Processor - Synchronous Main Application Entry Point
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings
from src.persistence.sync_database import SyncDatabaseManager
from src.data_ingestion.sync_feed_processor import SyncFeedProcessor

class RSSProcessorApp:
    def __init__(self):
        self.db_manager = SyncDatabaseManager()
        self.feed_processor = None
        
        # Configure logging
        log_level = settings.log_level
        logger.remove()  # Remove default handler
        logger.add(sys.stdout, level=log_level, format="{time} | {level} | {message}")
        
        if settings.log_file:
            Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
            logger.add(settings.log_file, level=log_level, rotation="10 MB")
    
    def initialize(self):
        """Initialize the application"""
        logger.info("Initializing RSS Processor...")
        
        # Create database tables
        self.db_manager.create_tables()
        
        # Initialize feed processor
        self.feed_processor = SyncFeedProcessor(
            db_manager=self.db_manager,
            max_articles_per_run=settings.max_articles_per_day,
            content_extraction=True
        )
        
        logger.info("Initialization complete")
    
    def test_scraper(self):
        """Test the Inoreader scraper"""
        logger.info("Testing Inoreader scraper...")
        
        if not self.feed_processor:
            self.initialize()
        
        try:
            # Test scraper functionality
            result = self.feed_processor.test_scraper()
            
            if result:
                logger.info("✓ Login successful")
                logger.info("✓ Scraper test completed successfully")
            else:
                logger.error("✗ Login failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Scraper test failed: {e}")
            logger.error(f"Application error: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="RSS Processor CLI")
    parser.add_argument(
        "command",
        choices=["init", "test", "process", "sync", "status"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    app = RSSProcessorApp()
    
    try:
        if args.command == "init":
            app.initialize()
        elif args.command == "test":
            app.test_scraper()
        elif args.command == "process":
            app.process_feeds()
        elif args.command == "sync":
            app.sync_feeds()
        elif args.command == "status":
            app.show_status()
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()