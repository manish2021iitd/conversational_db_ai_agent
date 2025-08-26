from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
from .nlp import classify_intent, extract_entities, sentiment
from .db import run_find, run_aggregate

def month_bounds(offset: int = 0):
    today = datetime.utcnow()
    first = today.replace(day=1) + timedelta(days=31*offset)
    first = first.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if offset == 0:
        next_month = (first + timedelta(days=31)).replace(day=1)
    else:
        next_month = (first + timedelta(days=31)).replace(day=1)
    return first, next_month

def time_filter(ent: Dict[str, Any]) -> Dict[str, Any]:
    tw = ent.get("time_window")
    if not tw: return {}
    if tw == "this_month":
        start, end = month_bounds(0)
    elif tw == "last_month":
        # set to previous month
        today = datetime.utcnow().replace(day=1) - timedelta(days=1)
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start + timedelta(days=31)).replace(day=1)
    elif tw == "last_6_months":
        end = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start = end - timedelta(days=180)
    elif tw.isdigit():
        start = datetime(int(tw), 1, 1)
        end = datetime(int(tw)+1, 1, 1)
    else:
        return {}
    return {"timestamp": {"$gte": start.isoformat(), "$lt": end.isoformat()}}

def handle_query(question: str) -> Tuple[str, pd.DataFrame, Dict[str, Any]]:
    intent = classify_intent(question)
    ent = extract_entities(question)
    s = sentiment(question)

    meta = {"intent": intent, "entities": ent, "sentiment": s}
    coll = ent.get("collection") or "transactions"

    # Definition
    if intent == "definition":
        if coll == "customers":
            df = run_find("customers", {}, {"_id":1,"name":1,"kyc":1,"address":1}, 50)
            answer = "Basic customer directory (first 50)."
            return answer, df, meta
        if coll == "accounts":
            df = run_find("accounts", {}, {"_id":1,"customer_id":1,"account_type":1,"balance":1,"status":1}, 50)
            return "Sample accounts (first 50).", df, meta
        # default
        df = run_find("transactions", {}, {"_id":1,"amount":1,"category":1,"merchant":1,"timestamp":1}, 50)
        return "Sample transactions (first 50).", df, meta

    # Trend (group by month)
    if intent == "trend":
        filt = time_filter(ent)
        pipeline = []
        if filt: pipeline.append({"$match": filt})
        pipeline += [
            {"$group": {
                "_id": {"$substr": ["$timestamp", 0, 7]},
                "total_amount": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        df = run_aggregate("transactions", pipeline)
        df.rename(columns={"_id":"month"}, inplace=True)
        return "Monthly trend of transaction totals.", df, meta

    # Comparison (e.g., compare by category or type)
    if intent == "comparison":
        groupby = ent.get("groupby") or "category"
        pipeline = [
            {"$group": {"_id": f"${groupby}", "total_amount": {"$sum":"$amount"}, "count":{"$sum":1}}},
            {"$sort": {"total_amount": -1}},
            {"$limit": ent.get("topk") or 10}
        ]
        df = run_aggregate("transactions", pipeline)
        df.rename(columns={"_id":groupby}, inplace=True)
        return f"Comparison by {groupby}.", df, meta

    # Aggregate (sum/avg/top)
    if intent == "aggregate":
        groupby = ent.get("groupby") or "merchant"
        filt = {}
        tf = time_filter(ent)
        if tf: filt.update(tf)
        if ent.get("field") == "category" and ent.get("value"):
            filt["category"] = ent["value"]
        pipeline = []
        if filt: pipeline.append({"$match": filt})
        pipeline += [
            {"$group": {"_id": f"${groupby}", "total_amount": {"$sum":"$amount"}, "count": {"$sum":1}}},
            {"$sort": {"total_amount": -1}},
            {"$limit": ent.get("topk") or 10}
        ]
        df = run_aggregate("transactions", pipeline)
        df.rename(columns={"_id":groupby}, inplace=True)
        return f"Top {ent.get('topk') or 10} by {groupby}.", df, meta

    # Filter (default)
    filt = {}
    if ent.get("field") and ent.get("value"):
        key = ent["field"]
        if key in ["city","address.city","location.city"]:
            filt["location.city"] = ent["value"].capitalize()
        else:
            # naive mapping
            keymap = {"account_type":"account_type","risk":"kyc.risk_score","risk_score":"kyc.risk_score"}
            mongo_key = keymap.get(key, key)
            filt[mongo_key] = ent["value"]
    tf = time_filter(ent)
    if tf: filt.update(tf)
    projection = None
    if coll == "transactions":
        projection = {"_id":1,"amount":1,"merchant":1,"category":1,"timestamp":1,"status":1}
    df = run_find(coll, filt, projection, 50)
    return "Matching records.", df, meta
