# src/utils/database.py
import sqlite3
from datetime import datetime, date
from pathlib import Path
import json

class BotDatabase:
    def __init__(self, db_path='data/bots.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bot execution history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_name TEXT NOT NULL,
                run_time TIMESTAMP NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                platform TEXT,
                error TEXT,
                duration_ms INTEGER
            )
        ''')
        
        # Bot state
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_state (
                bot_name TEXT PRIMARY KEY,
                last_run TIMESTAMP,
                run_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                state_json TEXT
            )
        ''')
        
        # Events table - generic storage for all event types
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_date DATE NOT NULL,
                event_time TIME,
                title TEXT NOT NULL,
                description TEXT,
                metadata TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bin collection schedule
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bin_collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_date DATE NOT NULL,
                bin_type TEXT NOT NULL,
                notes TEXT,
                is_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bot_runs_bot_name 
            ON bot_runs(bot_name)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_events_date 
            ON events(event_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_events_type 
            ON events(event_type)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bin_collections_date 
            ON bin_collections(collection_date)
        ''')
        
        conn.commit()
        conn.close()
    
    # ========== Bot Run Logging ==========
    
    def log_run(self, bot_name, status, message=None, platform=None, 
                error=None, duration_ms=None):
        """Log a bot execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bot_runs 
            (bot_name, run_time, status, message, platform, error, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (bot_name, datetime.now(), status, message, platform, 
              error, duration_ms))
        
        cursor.execute('''
            INSERT INTO bot_state (bot_name, last_run, run_count, 
                                  success_count, failure_count)
            VALUES (?, ?, 1, ?, ?)
            ON CONFLICT(bot_name) DO UPDATE SET
                last_run = ?,
                run_count = run_count + 1,
                success_count = success_count + ?,
                failure_count = failure_count + ?
        ''', (
            bot_name, datetime.now(),
            1 if status == 'success' else 0,
            1 if status == 'failed' else 0,
            datetime.now(),
            1 if status == 'success' else 0,
            1 if status == 'failed' else 0
        ))
        
        conn.commit()
        conn.close()
    
    def get_bot_stats(self, bot_name):
        """Get statistics for a bot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT last_run, run_count, success_count, failure_count
            FROM bot_state WHERE bot_name = ?
        ''', (bot_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'last_run': result[0],
                'run_count': result[1],
                'success_count': result[2],
                'failure_count': result[3]
            }
        return None
    
    # ========== Generic Events ==========
    
    def add_event(self, event_type, event_date, title, description=None, 
                  event_time=None, metadata=None):
        """Add a generic event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO events 
            (event_type, event_date, event_time, title, description, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_type, event_date, event_time, title, description, metadata_json))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id
    
    def get_events(self, event_type=None, start_date=None, end_date=None, 
                   is_active=True):
        """Get events, optionally filtered"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM events WHERE is_active = ?'
        params = [is_active]
        
        if event_type:
            query += ' AND event_type = ?'
            params.append(event_type)
        
        if start_date:
            query += ' AND event_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND event_date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY event_date ASC'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_upcoming_events(self, event_type=None, days=7):
        """Get upcoming events in the next N days"""
        today = date.today()
        end_date = date.today().replace(day=today.day + days)
        return self.get_events(event_type, start_date=today, end_date=end_date)
    
    # ========== Bin Collections ==========
    
    def add_bin_collection(self, collection_date, bin_type, notes=None):
        """Add a bin collection event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bin_collections 
            (collection_date, bin_type, notes)
            VALUES (?, ?, ?)
        ''', (collection_date, bin_type, notes))
        
        collection_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return collection_id
    
    def get_bin_collections(self, start_date=None, end_date=None, 
                           bin_type=None, is_completed=False):
        """Get bin collections, optionally filtered"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM bin_collections WHERE is_completed = ?'
        params = [is_completed]
        
        if start_date:
            query += ' AND collection_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND collection_date <= ?'
            params.append(end_date)
        
        if bin_type:
            query += ' AND bin_type = ?'
            params.append(bin_type)
        
        query += ' ORDER BY collection_date ASC'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_next_bin_collection(self, bin_type=None):
        """Get the next upcoming bin collection"""
        today = date.today()
        collections = self.get_bin_collections(
            start_date=today, 
            bin_type=bin_type, 
            is_completed=False
        )
        return collections[0] if collections else None
    
    def mark_bin_collection_completed(self, collection_id):
        """Mark a bin collection as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE bin_collections 
            SET is_completed = 1 
            WHERE id = ?
        ''', (collection_id,))
        
        conn.commit()
        conn.close()
    
    def bulk_add_bin_collections(self, collections):
        """
        Add multiple bin collections at once.
        collections: list of tuples (collection_date, bin_type, notes)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.executemany('''
            INSERT INTO bin_collections 
            (collection_date, bin_type, notes)
            VALUES (?, ?, ?)
        ''', collections)
        
        conn.commit()
        conn.close()

# Singleton instance
db = BotDatabase()
