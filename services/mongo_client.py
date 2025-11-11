"""
MongoDB client utility for optional data storage.
Initializes a global connection and provides safe insert helpers.
"""

from typing import Dict, Optional
import os
from pymongo import MongoClient

_mongo_client: Optional[MongoClient] = None
_mongo_db = None


def init_mongo(uri: str) -> bool:
    """Initialize MongoDB client using provided URI. Returns True if ready."""
    global _mongo_client, _mongo_db
    try:
        if not uri:
            print("[Mongo] No URI provided; Mongo disabled")
            return False
        if not uri.startswith("mongodb"):
            print(f"[Mongo] URI does not look like MongoDB: {uri}")
            return False

        _mongo_client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        # Trigger a server selection to verify connectivity
        _mongo_client.admin.command('ping')

        # Use default database from URI if present; else fallback
        try:
            _mongo_db = _mongo_client.get_default_database()
        except Exception:
            # Fallback to database name env or hardcoded default
            db_name = os.getenv('MONGO_DB_NAME', 'early_warning_system')
            _mongo_db = _mongo_client[db_name]

        print(f"[Mongo] Connected to DB: {_mongo_db.name}")
        return True
    except Exception as e:
        print(f"[Mongo] Initialization failed: {e}")
        _mongo_client = None
        _mongo_db = None
        return False


def get_db():
    """Return the initialized Mongo database or None."""
    return _mongo_db


def insert_chat_interaction(doc: Dict) -> bool:
    """Insert a chat interaction document into Mongo, return success."""
    try:
        if _mongo_db is None:
            return False
        _mongo_db['chat_interactions'].insert_one(doc)
        return True
    except Exception as e:
        print(f"[Mongo] insert_chat_interaction failed: {e}")
        return False


def insert_alert(doc: Dict) -> bool:
    """Insert an alert document into Mongo, return success."""
    try:
        if _mongo_db is None:
            return False
        _mongo_db['alerts'].insert_one(doc)
        return True
    except Exception as e:
        print(f"[Mongo] insert_alert failed: {e}")
        return False