from mako.template import Template
from mako.lookup import TemplateLookup
import logging
import pytz
from datetime import datetime
from ..config.settings import TEMPLATE_DIR, HTML_OUTPUT_FILE, TIMEZONE, ENVIRONMENT

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
            
            html_content = template.render(
                items=items,
                last_update_time=current_time,
                environment=ENVIRONMENT
            )
            
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