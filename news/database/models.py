import sqlite3
from datetime import datetime
import logging
from ..config.settings import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(DATABASE_PATH)
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        cursor = self.conn.cursor()
        cursor.execute('''
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
        self.conn.commit()

    def save_items(self, items):
        """Save or update news items in the database"""
        cursor = self.conn.cursor()
        for item in items:
            try:
                # Check if item exists
                cursor.execute('SELECT id FROM news_items WHERE id = ?', (item['id'],))
                if cursor.fetchone() is None:
                    # Insert new item
                    cursor.execute('''
                        INSERT INTO news_items 
                        (id, title, link, source, pub_date, description, image_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item['id'],
                        item['title'],
                        item['link'],
                        item['source'],
                        item['pub_date'],
                        item['description'],
                        item['image_url']
                    ))
                else:
                    # Update existing item
                    cursor.execute('''
                        UPDATE news_items 
                        SET title = ?, pub_date = ?, description = ?, image_url = ?
                        WHERE id = ?
                    ''', (
                        item['title'],
                        item['pub_date'],
                        item['description'],
                        item['image_url'],
                        item['id']
                    ))
            except sqlite3.IntegrityError as e:
                logger.warning(f"Integrity error for item {item['id']}: {str(e)}")
                continue

        self.conn.commit()

    def get_recent_items(self, limit=500):
        """Get recent news items from the database"""
        cursor = self.conn.cursor()
        return cursor.execute('''
            SELECT *, datetime(pub_date) as formatted_date 
            FROM news_items 
            ORDER BY pub_date DESC 
            LIMIT ?
        ''', (limit,)).fetchall()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close() 