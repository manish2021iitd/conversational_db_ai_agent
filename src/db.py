import os
from typing import Any, Dict, List, Optional, Tuple
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def get_client() -> MongoClient:
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    return MongoClient(uri, serverSelectionTimeoutMS=4000)

def get_db():
    client = get_client()
    dbname = os.getenv("MONGODB_DB", "finance_chat")
    return client[dbname]

def healthcheck() -> Tuple[bool, str]:
    try:
        client = get_client()
        client.admin.command("ping")
        return True, "MongoDB connection OK"
    except ConnectionFailure as e:
        return False, f"MongoDB connection failed: {e}"

def df_from_cursor(cur) -> pd.DataFrame:
    rows = list(cur)
    if not rows:
        return pd.DataFrame()
    for r in rows:
        r["_id"] = str(r.get("_id"))
    return pd.DataFrame(rows)

def run_find(collection: str, filter_q: Dict, projection: Optional[Dict] = None, limit: int = 50):
    db = get_db()
    cur = db[collection].find(filter_q, projection).limit(limit)
    return df_from_cursor(cur)

def run_aggregate(collection: str, pipeline: List[Dict]):
    db = get_db()
    cur = db[collection].aggregate(pipeline)
    return df_from_cursor(cur)

def collections_exist(names: List[str]) -> Dict[str, bool]:
    db = get_db()
    existing = set(db.list_collection_names())
    return {n: n in existing for n in names}
