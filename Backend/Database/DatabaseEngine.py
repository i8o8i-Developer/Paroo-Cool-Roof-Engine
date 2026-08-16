"""
Database Engine Module For PARoo Geospatial Intelligence Platform
Manages Thread-Safe SQLite Connection Pooling, WAL Mode, And Schema Creation.
"""

import os
import sqlite3
from typing import Generator
from contextlib import contextmanager
from ..Utils.TitleCaseLogger import LogInfo, LogWarning, LogError

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Data")
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_FILE_PATH = os.path.join(DATABASE_DIR, "PARooProductionDatabase.sqlite")

def GetDatabaseConnection() -> sqlite3.Connection:
    """Create And Configure A High-Performance SQLite Connection With WAL Mode."""
    Conn = sqlite3.connect(DATABASE_FILE_PATH, check_same_thread=False, timeout=30.0)
    Conn.row_factory = sqlite3.Row
    # Enable WAL Mode (Write-Ahead Logging) For High Concurrency
    Conn.execute("PRAGMA journal_mode = WAL;")
    Conn.execute("PRAGMA synchronous = NORMAL;")
    Conn.execute("PRAGMA foreign_keys = ON;")
    Conn.execute("PRAGMA cache_size = -64000;")  # 64MB In-Memory Cache
    return Conn

@contextmanager
def GetDatabaseCursor() -> Generator[sqlite3.Cursor, None, None]:
    """Context Manager Yielding An Active Database Cursor With Automatic Commit/Rollback."""
    Conn = GetDatabaseConnection()
    Cursor = Conn.cursor()
    try:
        yield Cursor
        Conn.commit()
    except Exception as Ex:
        Conn.rollback()
        LogError(f"Database Transaction Failed: {str(Ex)}")
        raise Ex
    finally:
        Cursor.close()
        Conn.close()
