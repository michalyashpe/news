import logging
import threading
import time
import json
import os
from flask import Flask, send_file, request, render_template_string
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from config.settings import (
    DEFAULT_PORT, STATIC_DIR, LAST_RUN_FILE, TIMEZONE,
    UPDATE_INTERVAL, ERROR_RETRY_INTERVAL, HTML_OUTPUT_FILE,
    IS_PRODUCTION, IS_STAGING, IS_DEVELOPMENT, ENVIRONMENT
)
from database.models import Database
from feeds.fetcher import FeedFetcher
from services.html_generator import HTMLGenerator
from services.llm_service import LLMService

# Set up logging
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')

# Initialize services
try:
    db = Database()
    feed_fetcher = FeedFetcher()
    html_generator = HTMLGenerator()
    llm_service = LLMService()
    logger.info("Successfully initialized all services")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

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
    """Serve the generated HTML file or filtered news view"""
    try:
        # Check if source filter is applied
        source = request.args.get('source')
        
        if source:
            # If a source is specified, get filtered items from DB and render dynamic template
            recent_items = db.get_filtered_items(source)
            
            # Get current time in specified timezone
            tz = pytz.timezone(TIMEZONE)
            current_time = datetime.now(tz).strftime('%d/%m %H:%M')
            
            # Use the HTML generator to render with filtered items
            return html_generator.render_filtered(recent_items, current_time, source)
        
        # If no source filter, serve the static file
        if not os.path.exists(HTML_OUTPUT_FILE):
            logger.error(f"HTML file not found at {HTML_OUTPUT_FILE}")
            return "News page is being generated. Please try again in a few moments.", 503
        
        return send_file(HTML_OUTPUT_FILE)
    except Exception as e:
        logger.error(f"Error serving news: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/status')
def status():
    """Return the current status of the service"""
    try:
        if not os.path.exists(LAST_RUN_FILE):
            return {
                'status': 'initializing',
                'message': 'Service is starting up'
            }
        with open(LAST_RUN_FILE, 'r') as f:
            last_run = json.load(f)
        return {
            'status': 'running',
            'last_update': last_run['last_run'],
            'environment': 'production' if IS_PRODUCTION else 'staging' if IS_STAGING else 'development'
        }
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

@app.before_request
def start_background_thread_once():
    """Start the background update thread if it's not running"""
    global background_thread
    if background_thread is None or not background_thread.is_alive():
        try:
            background_thread = threading.Thread(target=update_news)
            background_thread.daemon = True
            background_thread.start()
            logger.info("Background update thread started or restarted")
        except Exception as e:
            logger.error(f"Failed to start background thread: {str(e)}")

def main():
    """Main entry point for the application"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        try:
            db.reset()
            print("Database reset successfully")
            return
        except Exception as e:
            print(f"Error resetting database: {str(e)}")
            return 1
    
    port = int(os.environ.get('PORT', DEFAULT_PORT))
    logger.info(f"Starting application in {ENVIRONMENT} environment on port {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main() 