from mako.template import Template
from mako.lookup import TemplateLookup
import logging
import pytz
from datetime import datetime
from config.settings import TEMPLATE_DIR, HTML_OUTPUT_FILE, TIMEZONE, ENVIRONMENT, FEEDS

logger = logging.getLogger(__name__)

class HTMLGenerator:
    def __init__(self):
        self.lookup = TemplateLookup(directories=[TEMPLATE_DIR])

    def generate(self, items):
        """Generate HTML file from news items"""
        try:
            template = self.lookup.get_template('news.mako')
            
            # Get current time in specified timezone
            tz = pytz.timezone(TIMEZONE)
            current_time = datetime.now(tz).strftime('%d/%m %H:%M')
            
            # Get list of available sources from the database
            from database.models import Database
            db = Database()
            available_sources = db.get_available_sources()
            
            logger.info(f"Generating HTML with environment: {ENVIRONMENT}")
            html_content = template.render(
                items=items,
                last_update_time=current_time,
                environment=ENVIRONMENT,
                feeds=FEEDS,
                available_sources=available_sources
            )
            
            # Log the favicon path being used
            favicon_path = f"/static/favicon{'-staging' if ENVIRONMENT == 'staging' else ''}.png"
            logger.info(f"Using favicon path: {favicon_path}")
            
            with open(HTML_OUTPUT_FILE, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.info("HTML file generated successfully")
            return True
        except Exception as e:
            logger.error(f"Error generating HTML: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Error traceback: {traceback.format_exc()}")
            return False
            
    def render_filtered(self, items, current_time, selected_source):
        """Render HTML directly for filtered news items"""
        try:
            template = self.lookup.get_template('news.mako')
            
            # Get list of available sources from the database
            from database.models import Database
            db = Database()
            available_sources = db.get_available_sources()
            
            html_content = template.render(
                items=items,
                last_update_time=current_time,
                environment=ENVIRONMENT,
                feeds=FEEDS,
                selected_source=selected_source,
                available_sources=available_sources
            )
            
            return html_content
        except Exception as e:
            logger.error(f"Error rendering filtered HTML: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Error traceback: {traceback.format_exc()}")
            return "Error generating filtered content", 500 