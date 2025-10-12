# setup_db.py
import os
import json
import logging
from pymongo import errors
from utils.db import get_collection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
SAMPLE_FILE = os.getenv("SAMPLE_FILE", "./sample/test_cases.json")

def create_index():
    coll = get_collection()
    try:
        coll.create_index("vuln_id", unique=True, name="uniq_vuln_id")
        logging.info("Unique index ensured on 'vuln_id'")
    except errors.PyMongoError as e:
        logging.error("Index creation failed: %s", e)
        raise

def load_sample(sample_path=SAMPLE_FILE):
    if not os.path.exists(sample_path):
        logging.warning("Sample file not found: %s", sample_path)
        return
    coll = get_collection()
    with open(sample_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    test_cases = data.get("test_cases", []) if isinstance(data, dict) else []
    docs = []
    for tc in test_cases:
        if isinstance(tc, dict) and tc.get("vuln_id"):
            docs.append(tc)
    if not docs:
        logging.warning("No valid test cases found in sample")
        return
    try:
        coll.insert_many(docs, ordered=False)
        logging.info("Inserted %d sample docs", len(docs))
    except errors.BulkWriteError as bwe:
        logging.warning("BulkWriteError during sample load: %s", bwe.details.get("writeErrors", []))
    except errors.PyMongoError as e:
        logging.error("DB error: %s", e)
        raise

if __name__ == "__main__":
    create_index()
    load_sample()
    logging.info("setup_db complete")
