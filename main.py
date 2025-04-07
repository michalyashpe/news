import feedparser
import sqlite3
from datetime import datetime
import hashlib
import sys
from openai import OpenAI
from mako.template import Template
from mako.lookup import TemplateLookup
from flask import Flask, send_file
import threading
import time
import os
import logging
import json
import pytz

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Replace with environment variables
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

def create_database():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS news_items')
    c.execute('''
        CREATE TABLE IF NOT EXISTS news_items (
            id TEXT PRIMARY KEY,
            title TEXT,
            link TEXT,
            source TEXT,
            pub_date DATETIME,
            description TEXT,
            image_url TEXT
        )
    ''')
    conn.commit()
    return conn

def get_feed_items():
    feeds = {
        'haaretz': 'https://www.haaretz.co.il/srv/rss---feedly',
        'ynet': 'https://www.ynet.co.il/Integration/StoryRss2.xml',
        'israel_hayom': 'https://www.israelhayom.co.il/rss.xml',
        'kipa': 'https://www.kipa.co.il/rss/',
        'maariv': 'https://www.maariv.co.il/Rss/RssFeedsArutzSheva',
        'walla': 'https://rss.walla.co.il/feed/1',
        # 'calcalist': 'https://www.calcalist.co.il/GeneralRss/0,16335,L-8,00.xml',
        # 'globes': 'https://www.globes.co.il/webservice/rss/rssfeeder.asmx/FeederNode?iID=585',
        'kan': 'https://www.kan.org.il/rss/',
        'makor_rishon': 'https://www.makorrishon.co.il/rss/'
    }
    
    items = []
    for source, url in feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Get image URL from media content or enclosures if available
            image_url = None
            # if 'image' in entry:
            #     image_url = entry.get('image', [])
            #     print(f"Image URL: {image_url}")
            # elif 'media_content' in entry:
            #     media_contents = entry.get('media_content', [])
            #     if media_contents and 'url' in media_contents[0]:
            #         image_url = media_contents[0]['url']
            # elif 'enclosures' in entry:
            #     enclosures = entry.get('enclosures', [])
            #     if enclosures and 'url' in enclosures[0]:
            #         image_url = enclosures[0]['url']

            item = {
                'title': entry.title,
                'link': entry.link,
                'source': source,
                'pub_date': entry.get('published', ''),
                'description': entry.get('description', ''),
                'image_url': image_url
            }
            # Create unique ID from content
            item_id = hashlib.md5(f"{item['title']}{item['link']}".encode()).hexdigest()
            item['id'] = item_id
            items.append(item)
    return items

def save_items(conn, items):
    c = conn.cursor()
    for item in items:
        # Parse the pub_date string to datetime
        try:
            if item['source'] == 'walla':
                # Handle Walla's GMT format
                parsed_date = datetime.strptime(item['pub_date'], '%a, %d %b %Y %H:%M:%S GMT')
            else:
                parsed_date = datetime.strptime(item['pub_date'], '%a, %d %b %Y %H:%M:%S %z')
        except ValueError as e:
            print(f"Date parsing error for {item['source']}: {item['pub_date']}")
            parsed_date = datetime.now()

        # Check if item already exists
        
        c.execute('SELECT id FROM news_items WHERE id = ?', (item['id'],))
        if c.fetchone() is None:
            # Get headlines from last 24 hours
            c.execute('''
                SELECT title FROM news_items 
                WHERE datetime(pub_date) >= datetime('now', '-1 day')
            ''')
            recent_headlines = [row[0] for row in c.fetchall()]
            
            # If there are recent headlines, check for new information
            # if recent_headlines:
            #     is_new_info = ask_llm(item['title'], recent_headlines)
            #     if is_new_info:
            #         print(f"New information detected in: {item['title']}")
            
            # Insert the new item
            c.execute('''
                INSERT INTO news_items 
                (id, title, link, source, pub_date, description, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['id'],
                item['title'],
                item['link'],
                item['source'],
                parsed_date.strftime('%Y-%m-%d %H:%M:%S'),
                item['description'],
                item['image_url']
            ))
        else:
            # Update if title has changed
            c.execute('''
                UPDATE news_items 
                SET title = ?, pub_date = ?, image_url = ?
                WHERE id = ?
            ''', (
                item['title'],
                parsed_date.strftime('%Y-%m-%d %H:%M:%S'),
                item['image_url'],
                item['id']
            ))
    conn.commit()

def ask_llm(new_headline, recent_headlines):
    client = OpenAI(
      base_url=OPENROUTER_BASE_URL,
      api_key=OPENROUTER_API_KEY,
    )
    content = f"You are a news reporter.\nYou need to answer in YES or NO. No other word is allowed.\nIs the following headline new information? {new_headline} \n\n Here are the recent headlines: {recent_headlines}"
    messages = [{"role": "user", "content": content}]
    print(f"Messages: {messages}")
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>",
            "X-Title": "<YOUR_SITE_NAME>",
        },
        # model="openai/gpt-4o",
        model="deepseek/deepseek-r1-zero:free",
        messages=messages
    )
    return completion.choices[0].message.content 

    # This is a placeholder function that will be implemented later
    # It should return True if the new headline contains new information
    # compared to the recent headlines
    pass

def print_all_items(conn):
    c = conn.cursor()
    for row in c.execute('SELECT * FROM news_items ORDER BY pub_date DESC'):
        print(f"Title: {row[1]}\nSource: {row[3]}\nLink: {row[2]}\n")

def generate_html(conn):
    c = conn.cursor()
    lookup = TemplateLookup(directories=['templates'])
    template = lookup.get_template('news.mako')
    
    items = c.execute('SELECT *, datetime(pub_date) as formatted_date FROM news_items ORDER BY pub_date DESC LIMIT 500').fetchall()
    html_content = template.render(items=items)
    
    with open('news.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def update_news_periodically():
    while True:
        try:
            israel_tz = pytz.timezone('Asia/Jerusalem')
            current_time = datetime.now(israel_tz).strftime('%d/%m/%Y %H:%M:%S')
            logger.info(f"Starting news update at {current_time}")
            
            conn = create_database()
            logger.info("Database created/connected")
            
            items = get_feed_items()
            logger.info(f"Fetched {len(items)} news items")
            
            save_items(conn, items)
            logger.info("Saved items to database")
            
            generate_html(conn)
            logger.info("Generated HTML file")
            
            conn.close()
            logger.info("Update completed successfully")
            
            # Save last run time
            with open('last_run.json', 'w', encoding='utf-8') as f:
                json.dump({'last_run': current_time}, f)
                
            time.sleep(30)  # Wait 30 seconds before next update
            
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
            time.sleep(5)  # Wait 5 seconds if there's an error

@app.route('/')
def serve_news():
    try:
        return send_file('news.html')
    except Exception as e:
        logger.error(f"Error serving news.html: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/status')
def status():
    try:
        with open('last_run.json', 'r') as f:
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

# Start the background thread when the app starts
@app.before_request
def start_background_thread():
    thread = threading.Thread(target=update_news_periodically)
    thread.daemon = True
    thread.start()
    logger.info("Background update thread started")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)