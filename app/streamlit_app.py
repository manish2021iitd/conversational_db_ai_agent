import streamlit as st
import pandas as pd
from src.agent import handle_query
from src.db import healthcheck, run_find
from src.memory import ConversationMemory
from src.world_model import data_gaps_summary, actionable_insights

st.set_page_config(page_title="Conversational DB Agent", layout="wide")
st.title("💬 Conversational Database Agent — Finance (MongoDB)")

ok, msg = healthcheck()
st.sidebar.subheader("Database")
st.sidebar.write("Status:", "✅" if ok else "⚠️", msg)

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

# Insights dashboard
st.sidebar.subheader("World Model Insights")
with st.sidebar:
    cust = run_find("customers", {}, limit=500)
    acc = run_find("accounts", {}, limit=500)
    txn = run_find("transactions", {}, limit=1000)
    gaps = data_gaps_summary(cust, acc, txn)
    for k,v in gaps.items():
        st.write(f"- **{k.replace('_',' ').title()}**: {v}")
    for tip in actionable_insights(gaps):
        st.caption("• " + tip)

st.markdown("Ask questions like *'Top 5 merchants by total debit this month'*, *'Trend of grocery spend by month'*, *'Compare average spend by category'*")

with st.form(key="chat"):
    q = st.text_input("Your question")
    submitted = st.form_submit_button("Ask")
if submitted and q:
    answer, table, meta = handle_query(q)
    st.success(answer)
    if not table.empty:
        st.dataframe(table, use_container_width=True)
    st.caption(f"Intent: `{meta['intent']}` | Sentiment: {meta['sentiment']:.2f} | Entities: {meta['entities']}")
