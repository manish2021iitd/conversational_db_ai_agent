import re
from typing import Dict, Any, Optional
from textblob import TextBlob

FIELDS = {
    "transactions": ["amount","category","merchant","type","timestamp","status","channel","location.city"],
    "accounts": ["balance","account_type","status","opened_at"],
    "customers": ["name.first","name.last","kyc.pan_verified","kyc.risk_score","address.city","age"]
}

AGG_KEYWORDS = ["avg","average","sum","total","count","max","min","top","trend","compare","comparison","distribution"]
TIME_WORDS = ["today","yesterday","week","month","quarter","year","last","past","this","recent","since"]

def sentiment(text: str) -> float:
    """Return polarity in [-1,1]."""
    return TextBlob(text).sentiment.polarity

def classify_intent(q: str) -> str:
    s = q.lower()
    if any(k in s for k in ["define","what is","who is","details of","information on"]) and "trend" not in s:
        return "definition"
    if any(k in s for k in ["trend","over time","by month","timeseries","daily","weekly","monthly"]):
        return "trend"
    if any(k in s for k in ["compare","versus","vs","comparison"]):
        return "comparison"
    if any(k in s for k in AGG_KEYWORDS):
        return "aggregate"
    return "filter"

def extract_entities(q: str) -> Dict[str, Any]:
    s = q.lower()
    ent: Dict[str, Any] = {"collection": None, "field": None, "value": None, "time_window": None, "groupby": None, "topk": None}
    # collection guess
    if any(w in s for w in ["transaction","spend","merchant","debit","credit","refund","upi","card"]):
        ent["collection"] = "transactions"
    elif any(w in s for w in ["account","balance","savings","current","loan"]):
        ent["collection"] = "accounts"
    elif any(w in s for w in ["customer","kyc","risk","age","city"]):
        ent["collection"] = "customers"

    # field/value extraction (very simple)
    m = re.search(r"(category|merchant|type|status|city|account type|account_type|balance|age|risk(?: score)?)\s*(?:is|=|:)?\s*([a-zA-Z0-9_]+)", s)
    if m:
        key = m.group(1).replace(" ", "_")
        ent["field"] = key
        ent["value"] = m.group(2)

    # top-k
    m = re.search(r"top\s+(\d+)", s)
    if m: ent["topk"] = int(m.group(1))

    # group by
    if "by merchant" in s: ent["groupby"] = "merchant"
    if "by category" in s: ent["groupby"] = "category"
    if "by month" in s: ent["groupby"] = "month"
    if "by city" in s: ent["groupby"] = "location.city"

    # time window (basic)
    if any(w in s for w in ["this month","current month"]):
        ent["time_window"] = "this_month"
    elif any(w in s for w in ["last month","previous month"]):
        ent["time_window"] = "last_month"
    elif any(w in s for w in ["last 6 months","past 6 months","six months"]):
        ent["time_window"] = "last_6_months"
    elif any(w in s for w in ["2023","2024","2025"]):
        m = re.search(r"(2023|2024|2025)", s)
        ent["time_window"] = m.group(1)

    return ent
