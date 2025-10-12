# utils/db.py
import os
from pymongo import MongoClient, errors

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "tcs_vuln_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "vuln_testcases")

_client = None

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # test connectivity
        try:
            _client.admin.command("ping")
        except errors.ServerSelectionTimeoutError:
            raise
    return _client

def get_collection():
    client = get_client()
    return client[DB_NAME][COLLECTION_NAME]
