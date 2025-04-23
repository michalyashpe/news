import os
from datetime import timedelta

# Database settings
DATABASE_PATH = 'news.db'

# Feed settings
FEEDS = {
    'haaretz': 'https://www.haaretz.co.il/srv/rss---feedly',
    'ynet': 'https://www.ynet.co.il/Integration/StoryRss2.xml',
    'israel_hayom': 'https://www.israelhayom.co.il/rss.xml',
    'kipa': 'https://www.kipa.co.il/rss/',
    'maariv': 'https://www.maariv.co.il/Rss/RssFeedsArutzSheva',
    'walla': 'https://rss.walla.co.il/feed/1',
    'kan': 'https://www.kan.org.il/rss/',
    'makor_rishon': 'https://www.makorrishon.co.il/rss/'
}

# Update settings
UPDATE_INTERVAL = timedelta(seconds=30)
ERROR_RETRY_INTERVAL = timedelta(seconds=5)

# LLM settings
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

# Application settings
DEFAULT_PORT = 5000
TEMPLATE_DIR = 'templates'
STATIC_DIR = 'static'
HTML_OUTPUT_FILE = 'news.html'
LAST_RUN_FILE = 'last_run.json'

# Timezone settings
TIMEZONE = 'Asia/Jerusalem' 