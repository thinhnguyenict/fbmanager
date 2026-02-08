#!/usr/bin/env python3
"""
FB Manager - Facebook Management Tool
Main application entry point
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', '/var/log/fbmanager/app.log')

# Create logs directory if it doesn't exist
log_dir = Path(LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class FBManager:
    """Main Facebook Manager class"""
    
    def __init__(self):
        self.fb_email = os.getenv('FB_EMAIL')
        self.fb_password = os.getenv('FB_PASSWORD')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        if not self.fb_email or not self.fb_password:
            logger.warning("Facebook credentials not configured in .env file")
    
    def run(self):
        """Main application logic"""
        logger.info("Starting FB Manager...")
        logger.info(f"Debug mode: {self.debug}")
        
        try:
            # Your main application logic here
            logger.info("FB Manager is running...")
            
            # Example: Keep the application running
            # while True:
            #     # Your automation tasks
            #     time.sleep(60)
            
            logger.info("FB Manager completed successfully")
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal, stopping...")
        except Exception as e:
            logger.error(f"Error in FB Manager: {e}", exc_info=True)
            raise


def main():
    """Entry point"""
    logger.info("=" * 50)
    logger.info("FB Manager - Facebook Management Tool")
    logger.info("=" * 50)
    
    try:
        manager = FBManager()
        manager.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
