import logging
import threading
import time
import json
import os
from flask import Flask, send_file
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .config.settings import (
    DEFAULT_PORT, STATIC_DIR, LAST_RUN_FILE, TIMEZONE,
    UPDATE_INTERVAL, ERROR_RETRY_INTERVAL, HTML_OUTPUT_FILE
)
from .database.models import Database
from .feeds.fetcher import FeedFetcher
from .services.html_generator import HTMLGenerator
from .services.llm_service import LLMService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.static_folder = STATIC_DIR

# Initialize services
db = Database()
feed_fetcher = FeedFetcher()
html_generator = HTMLGenerator()
llm_service = LLMService()

# Background thread variable
background_thread = None

def update_news():
    """Update news items and generate HTML"""
    while True:
        try:
            # Get current time in specified timezone
            tz = pytz.timezone(TIMEZONE)
            current_time = datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
            logger.info(f"Starting news update at {current_time}")
            
            # Fetch and process news items
            items = feed_fetcher.fetch_items()
            logger.info(f"Fetched {len(items)} news items")
            
            # Save items to database
            db.save_items(items)
            logger.info("Saved items to database")
            
            # Get recent items for HTML generation
            recent_items = db.get_recent_items()
            
            # Generate HTML
            if html_generator.generate(recent_items):
                logger.info("Generated HTML file")
                
                # Save last run time
                with open(LAST_RUN_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'last_run': current_time}, f)
                logger.info("Last run time saved")
            
            time.sleep(UPDATE_INTERVAL.total_seconds())
            
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            if hasattr(e, '__traceback__'):
                import traceback
                logger.error(f"Error traceback: {traceback.format_exc()}")
            time.sleep(ERROR_RETRY_INTERVAL.total_seconds())

@app.route('/')
def serve_news():
    """Serve the generated HTML file"""
    try:
        return send_file(HTML_OUTPUT_FILE)
    except Exception as e:
        logger.error(f"Error serving news.html: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/status')
def status():
    """Return the current status of the service"""
    try:
        with open(LAST_RUN_FILE, 'r') as f:
            last_run = json.load(f)
        return {
            'status': 'running',
            'last_update': last_run['last_run']
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

@app.before_request
def start_background_thread_once():
    """Start the background update thread if it's not running"""
    global background_thread
    if background_thread is None or not background_thread.is_alive():
        background_thread = threading.Thread(target=update_news)
        background_thread.daemon = True
        background_thread.start()
        logger.info("Background update thread started or restarted")

def main():
    """Main entry point for the application"""
    port = int(os.environ.get('PORT', DEFAULT_PORT))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main() 