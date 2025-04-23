import os
from datetime import timedelta

# Get the absolute path of the workspace root
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database settings
DATABASE_PATH = 'news.db'

# Feed settings
FEEDS = {
    'ynet': 'https://z.ynet.co.il/short/content/RSS/index.html',
    'הארץ': 'https://www.haaretz.co.il/srv/rss---feedly',
    'ישראל היום': 'https://www.israelhayom.co.il/rss.xml',
    'מקור ראשון': 'https://www.makorrishon.co.il/feed/',
    'וואלה': 'https://rss.walla.co.il/feed/22',
    'כיפה': 'https://www.kipa.co.il/feed/%D7%97%D7%93%D7%A9%D7%95%D7%AA/',
    'מעריב': 'https://www.maariv.co.il/Rss/RssChadashot',
    'זמן ישראל': 'https://www.zman.co.il/feed/',
    'N12': 'https://www.mako.co.il/rss/31750a2610f26110VgnVCM1000005201000aRCRD.xml'
    # 'ערוץ 7': 'https://www.inn.co.il/Rss.aspx', //# links not wokrind
    # 'וואלה': 'https://rss.walla.co.il/feed/1?type=main', more general rss feed
    # 'המחדש': 'not found',
    # 'כאן': 'https://www.kan.org.il/headlines/'//no rss link found
    # 'n13: not found
    # 'c14': ' not found',
    # 'סרוגים': '',
    # '0404': '',
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
HTML_OUTPUT_FILE = os.path.join(WORKSPACE_ROOT, 'news.html')
LAST_RUN_FILE = 'last_run.json'

# Timezone settings
TIMEZONE = 'Asia/Jerusalem' 