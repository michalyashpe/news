import sqlite3
from datetime import datetime
import logging
import threading
from ..config.settings import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self._local = threading.local()
        self._create_tables()

    def _get_connection(self):
        """Get or create a database connection for the current thread"""
        if not hasattr(self._local, 'conn'):
            try:
                self._local.conn = sqlite3.connect(DATABASE_PATH)
                self._local.conn.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                logger.error(f"Database connection error: {str(e)}")
                raise
        return self._local.conn

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_items (
                id TEXT PRIMARY KEY,
                title TEXT,
                link TEXT,
                source TEXT,
                pub_date DATETIME,
                description TEXT,
                image_url TEXT,
                UNIQUE(source, title)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seen_ids (
                id TEXT PRIMARY KEY,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

    def save_items(self, items):
        """Save or update news items in the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
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

        conn.commit()

    def get_recent_items(self, limit=500):
        """Get recent news items from the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        return cursor.execute('''
            SELECT *, datetime(pub_date) as formatted_date 
            FROM news_items 
            ORDER BY pub_date DESC 
            LIMIT ?
        ''', (limit,)).fetchall()

    def close(self):
        """Close database connection for the current thread"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            delattr(self._local, 'conn')

    def reset(self):
        """Reset the database by dropping and recreating all tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Drop existing tables
            cursor.execute('DROP TABLE IF EXISTS news_items')
            cursor.execute('DROP TABLE IF EXISTS seen_ids')
            conn.commit()
            
            # Recreate tables with new schema
            self._create_tables()
            logger.info("Database reset successfully")
        except sqlite3.Error as e:
            logger.error(f"Error resetting database: {str(e)}")
            conn.rollback()
            raise 