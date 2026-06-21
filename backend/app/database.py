import aiosqlite
from pathlib import Path
from typing import Optional
import json

from app.config import settings


class Database:
    _instance: Optional["Database"] = None
    _db: Optional[aiosqlite.Connection] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def init_db(cls):
        db_path = settings.db_full_path
        db_path.parent.mkdir(parents=True, exist_ok=True)

        cls._db = await aiosqlite.connect(str(db_path))
        cls._db.row_factory = aiosqlite.Row
        await cls._create_tables()
        await cls._create_indexes()
        await cls._db.commit()

    @classmethod
    async def close(cls):
        if cls._db:
            await cls._db.close()
            cls._db = None

    @classmethod
    async def _create_tables(cls):
        await cls._db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT '',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                model TEXT DEFAULT '',
                total_tokens INTEGER DEFAULT 0,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0,
                source_file TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                raw_data TEXT NOT NULL,
                scanned_at REAL NOT NULL
            )
        """)

        await cls._db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                model TEXT DEFAULT '',
                created_at REAL NOT NULL,
                tokens INTEGER DEFAULT 0,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                message_index INTEGER NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)

    @classmethod
    async def _create_indexes(cls):
        await cls._db.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at)
        """)
        await cls._db.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions(updated_at)
        """)
        await cls._db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)
        """)
        await cls._db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)
        """)

    @classmethod
    async def get_connection(cls) -> aiosqlite.Connection:
        if cls._db is None:
            await cls.init_db()
        return cls._db

    @classmethod
    async def execute(cls, sql: str, params: tuple = ()):
        conn = await cls.get_connection()
        cursor = await conn.execute(sql, params)
        await conn.commit()
        return cursor

    @classmethod
    async def fetchall(cls, sql: str, params: tuple = ()):
        conn = await cls.get_connection()
        cursor = await conn.execute(sql, params)
        return await cursor.fetchall()

    @classmethod
    async def fetchone(cls, sql: str, params: tuple = ()):
        conn = await cls.get_connection()
        cursor = await conn.execute(sql, params)
        return await cursor.fetchone()


db = Database()
