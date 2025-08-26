from typing import Dict, Any, List
import pandas as pd

def data_gaps_summary(customers: pd.DataFrame, accounts: pd.DataFrame, transactions: pd.DataFrame) -> Dict[str, Any]:
    gaps = {}
    if not customers.empty:
        gaps["missing_kyc"] = int((~customers["kyc"].apply(lambda x: x.get("pan_verified", False))).sum())
        gaps["high_risk_customers"] = int(customers["kyc"].apply(lambda x: x.get("risk_score", 0) > 0.7).sum())
    if not accounts.empty:
        gaps["frozen_accounts"] = int((accounts["status"] == "frozen").sum())
    if not transactions.empty:
        gaps["pending_txn"] = int((transactions["status"] == "pending").sum())
        gaps["reversed_txn"] = int((transactions["status"] == "reversed").sum())
    return gaps

def actionable_insights(gaps: Dict[str, Any]) -> List[str]:
    out = []
    if gaps.get("missing_kyc", 0) > 0:
        out.append("Initiate KYC completion campaigns for customers without PAN verification.")
    if gaps.get("high_risk_customers", 0) > 0:
        out.append("Increase monitoring or set tighter limits for high risk score customers (>0.7).")
    if gaps.get("frozen_accounts", 0) > 0:
        out.append("Review frozen accounts for potential reactivation or closure.")
    if gaps.get("pending_txn", 0) > 0:
        out.append("Investigate stuck/pending transactions to improve customer experience.")
    if gaps.get("reversed_txn", 0) > 0:
        out.append("Analyze reversed transactions to reduce operational errors/chargebacks.")
    if not out:
        out.append("No critical gaps detected. Continue routine monitoring.")
    return out
