# Conversational Database AI Agent 
An end-to-end conversational agent that understands natural language questions about a **real MongoDB** finance-like database, translates them into MongoDB queries, executes them across **multiple collections**, maintains **conversation context**, and returns clear answers with **insights** (data gaps, sentiment, intent).

## Features

- **Database integration**: Works with MongoDB Atlas or local MongoDB.
- **Query types**: definitions, filters, aggregations, trends, comparisons, top-K, time ranges.
- **Multi-collection joins** (customer ↔ accounts ↔ transactions).
- **Context memory**: tracks follow-ups referring to prior results.
- **Vector search**: optional FAISS + transformer embeddings for schema/FAQ relevance.
- **World Model insights**: flags data gaps, surfaces objective actionable insights, and analyzes user tone.
- **UI**: Streamlit chat app with optional voice (STT/TTS via `streamlit-webrtc`).
- **Error handling**: detects ambiguous/impossible queries and asks for clarification.
- **Dockerized** for easy deployment.
- **Colab Notebook** for end-to-end demo (including synthetic dataset loading).

## Collections

- `customers` — nested fields, KYC, risk score
- `accounts` — balances, limits, type
- `transactions` — high-volume (≈900 docs), categories, merchants, timestamps

> We ship **synthetic datasets** in `data/` and a `scripts/seed_db.py` to load them into your MongoDB (Atlas or local).

## Quickstart

### 1) Environment
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in values
```

### 2) Seed the database
```bash
python scripts/seed_db.py  # loads data/* into MongoDB
```

### 3) Run the app
```bash
streamlit run app/streamlit_app.py
```

### 4) Docker (optional)
```bash
docker build -t convdb-agent .
docker run -p 8501:8501 --env-file .env convdb-agent
```

## Configuration

Set these in `.env`:
```
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>/
MONGODB_DB=finance_chat
OPENAI_API_KEY=sk-...                # optional
GEMINI_API_KEY=...                   # optional
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

If `MONGODB_URI` is not provided, the app attempts `mongodb://localhost:27017`.

## How it works

- `src/agent.py`: classifies **intent** (definition/filter/aggregate/trend/compare) and extracts entities (fields, values, time windows).
- `src/db.py`: builds and runs **MongoDB** queries from intents and maintains simple query templates.
- `src/memory.py`: tracks past turns and slot-fills missing context.
- `src/world_model.py`: computes **insights** (data gaps, anomalies) and sentiment.
- `src/vector_store.py`: builds a tiny vector index for schema + example Q/A for semantic recall.
- `app/streamlit_app.py`: the chat UI + voice; shows results tables and charts.

## Colab

Open `notebooks/colab_demo.ipynb` (or upload to Colab) for a fully runnable demo: seeding, sample questions, and evaluation.

## Example questions

- *What is the average transaction amount for shopping this month?*
- *Top 5 merchants by total debit in 2024?*
- *Show trend of grocery spend by month for the last 6 months.*
- *Compare average balance between savings and current accounts.*
- *Total refunds for customers in Mumbai with risk_score > 0.7.*
- *Who is Manish’s bank and what is his KYC status?* (definition + join)

## World Model Insights Dashboard

The Streamlit sidebar summarizes:
- Data coverage and gaps (e.g., missing KYC, frozen accounts, sparse merchants).
- User sentiment and intent mix over the session.
- Suggested data to collect next.

## Secondary/Bonus plan (design writeup)

If limited on time, see **docs in README bottom** for how to extend with:
- RAG over schema docs and business glossary.
- Advanced agentic reasoning with toolformer-like self-queries.
- Query optimization via index suggestions & explain plans.
- Better voice UX, diarization, and non-English support.

### What I'd build next (brief ideas)
- Add Guardrails for PII masking and rate limiting.
- Add temporal joins (sessionization) and cohorting.
- Add GLM-based semantic parser with program-of-thought outputs.
- Auto-generate Mongo indices from workload heatmap.
- Multi-tenant auth and per-tenant memory namespaces.

Dataset files: inside `data/`. You may upload them to cloud storage and paste the link here as required.
