"""
Database - SQLite database for storing reports and cached results
Handles all database operations asynchronously
"""

import aiosqlite
import json
from typing import Optional, Dict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "realityfix.db"):
        self.db_path = db_path
        self._initialized = False
    
    async def initialize(self):
        """Initialize database and create tables"""
        if self._initialized:
            return
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create reports table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS reports (
                        report_id TEXT PRIMARY KEY,
                        content_type TEXT NOT NULL,
                        content TEXT,
                        result TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Create user flags table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS user_flags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        report_id TEXT NOT NULL,
                        flag_type TEXT NOT NULL,
                        comment TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (report_id) REFERENCES reports (report_id)
                    )
                """)
                
                # Create cache table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS cache (
                        cache_key TEXT PRIMARY KEY,
                        cache_value TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT
                    )
                """)
                
                # Create indexes
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_reports_created 
                    ON reports(created_at)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_flags_report 
                    ON user_flags(report_id)
                """)
                
                await db.commit()
                
            self._initialized = True
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    async def save_report(self, report_id: str, content_type: str, 
                         content: str, result: Dict) -> bool:
        """
        Save analysis report to database
        
        Args:
            report_id: Unique report identifier
            content_type: Type of content (text, image, audio)
            content: Original content or URL
            result: Analysis result dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.initialize()
            
            now = datetime.utcnow().isoformat()
            result_json = json.dumps(result)
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO reports (report_id, content_type, content, result, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (report_id, content_type, content, result_json, now, now))
                
                await db.commit()
            
            logger.info(f"Report saved: {report_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return False
    
    async def get_report(self, report_id: str) -> Optional[Dict]:
        """
        Retrieve report by ID
        
        Args:
            report_id: Report identifier
            
        Returns:
            Report dictionary or None if not found
        """
        try:
            await self.initialize()
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                async with db.execute("""
                    SELECT * FROM reports WHERE report_id = ?
                """, (report_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if row:
                        return {
                            'report_id': row['report_id'],
                            'content_type': row['content_type'],
                            'content': row['content'],
                            'result': json.loads(row['result']),
                            'created_at': row['created_at'],
                            'updated_at': row['updated_at']
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get report: {e}")
            return None
    
    async def add_user_flag(self, report_id: str, flag_type: str, 
                           comment: Optional[str] = None) -> bool:
        """
        Add user flag to a report
        
        Args:
            report_id: Report to flag
            flag_type: Type of flag (incorrect, misleading, etc.)
            comment: Optional user comment
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.initialize()
            
            now = datetime.utcnow().isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO user_flags (report_id, flag_type, comment, created_at)
                    VALUES (?, ?, ?, ?)
                """, (report_id, flag_type, comment, now))
                
                await db.commit()
            
            logger.info(f"Flag added to report: {report_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add flag: {e}")
            return False
    
    async def get_cache(self, cache_key: str) -> Optional[str]:
        """
        Get cached value
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached value or None
        """
        try:
            await self.initialize()
            
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT cache_value, expires_at FROM cache 
                    WHERE cache_key = ?
                """, (cache_key,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if row:
                        cache_value, expires_at = row
                        
                        # Check expiration
                        if expires_at:
                            if datetime.fromisoformat(expires_at) < datetime.utcnow():
                                return None
                        
                        return cache_value
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cache: {e}")
            return None
    
    async def set_cache(self, cache_key: str, cache_value: str, 
                       ttl_seconds: Optional[int] = None) -> bool:
        """
        Set cached value
        
        Args:
            cache_key: Cache key
            cache_value: Value to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.initialize()
            
            now = datetime.utcnow()
            created_at = now.isoformat()
            expires_at = None
            
            if ttl_seconds:
                from datetime import timedelta
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO cache (cache_key, cache_value, created_at, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (cache_key, cache_value, created_at, expires_at))
                
                await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            await self.initialize()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
            
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False