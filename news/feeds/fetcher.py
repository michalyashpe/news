import feedparser
import hashlib
import logging
from datetime import datetime
from ..config.settings import FEEDS

logger = logging.getLogger(__name__)

class FeedFetcher:
    def __init__(self):
        self.seen_ids = set()

    def _generate_item_id(self, source, title, link, pub_date):
        """Generate a unique ID for a news item"""
        id_string = f"{source}:{title}:{link}:{pub_date}"
        return hashlib.md5(id_string.encode()).hexdigest()

    def _parse_date(self, date_str, source):
        """Parse date string based on source format"""
        try:
            if source == 'walla':
                return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
            return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        except ValueError as e:
            logger.warning(f"Date parsing error for {source}: {date_str}")
            return datetime.now()

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

                        if item_id in self.seen_ids:
                            logger.debug(f"Skipping duplicate item: {entry.title}")
                            continue
                        self.seen_ids.add(item_id)

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