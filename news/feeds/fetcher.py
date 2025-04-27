import feedparser
import hashlib
import logging
from datetime import datetime
from ..config.settings import FEEDS
from ..database.models import Database
import sqlite3

logger = logging.getLogger(__name__)

class FeedFetcher:
    def __init__(self):
        self.db = Database()
        self.date_formats = [
            '%a, %d %b %Y %H:%M:%S %z',  # Standard timezone format
            '%a, %d %b %Y %H:%M:%S GMT',  # GMT format
            '%a, %d %b %Y %H:%M:%S',      # No timezone format
            '%Y-%m-%dT%H:%M:%S%z',        # ISO format with timezone
            '%Y-%m-%dT%H:%M:%S'           # ISO format without timezone
        ]

    def _generate_item_id(self, source, title, link, pub_date):
        """Generate a unique ID for a news item"""
        # Normalize the title by removing extra spaces and converting to lowercase
        normalized_title = ' '.join(title.lower().split())
        # Use a combination of source and normalized title for better uniqueness
        id_string = f"{source}:{normalized_title}"
        return hashlib.md5(id_string.encode()).hexdigest()

    def _is_seen(self, item_id):
        """Check if an item ID has been seen before"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM seen_ids WHERE id = ?', (item_id,))
        return cursor.fetchone() is not None

    def _mark_seen(self, item_id):
        """Mark an item ID as seen"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT OR REPLACE INTO seen_ids (id) VALUES (?)', (item_id,))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error marking item as seen: {str(e)}")
            conn.rollback()

    def _parse_date(self, date_str, source):
        """Parse date string based on source format"""
        parsed_date = None
        
        for date_format in self.date_formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                break  # If parsing succeeds, break the loop
            except ValueError:
                continue
        
        if parsed_date is None:
            logger.warning(f"Date parsing error for {source}: {date_str}")
            parsed_date = datetime.now()
            
        return parsed_date

    def _extract_image_url(self, entry):
        """Extract image URL from feed entry"""
        if 'media_content' in entry:
            media_contents = entry.get('media_content', [])
            if media_contents and 'url' in media_contents[0]:
                return media_contents[0]['url']
        elif 'enclosures' in entry:
            enclosures = entry.get('enclosures', [])
            if enclosures and 'url' in enclosures[0]:
                return enclosures[0]['url']
        return None

    def fetch_items(self):
        """Fetch and process items from all configured feeds"""
        items = []
        
        for source, url in FEEDS.items():
            try:
                feed = feedparser.parse(url)
                if not feed.entries:
                    logger.warning(f"No entries found in feed: {source}")
                    continue

                for entry in feed.entries:
                    try:
                        pub_date = self._parse_date(entry.get('published', ''), source)
                        item_id = self._generate_item_id(
                            source, 
                            entry.title, 
                            entry.link, 
                            entry.get('published', '')
                        )

                        if self._is_seen(item_id):
                            logger.debug(f"Skipping duplicate item: {entry.title}")
                            continue
                        self._mark_seen(item_id)

                        item = {
                            'id': item_id,
                            'title': entry.title,
                            'link': entry.link,
                            'source': source,
                            'pub_date': pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'description': entry.get('description', ''),
                            'image_url': self._extract_image_url(entry)
                        }
                        items.append(item)
                    except Exception as e:
                        logger.error(f"Error processing entry in feed {source}: {str(e)}")
                        continue
            except Exception as e:
                logger.error(f"Error processing feed {source}: {str(e)}")
                continue

        return items 