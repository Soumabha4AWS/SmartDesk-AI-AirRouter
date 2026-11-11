# Smart Desk AI — README

A walk-through of each component and how to run the project.

## 1) Overview
Smart Desk AI is a LangGraph-based multi-agent system for HR/IT support with Retrieval-Augmented Generation (RAG), ticket status lookup, and ticket escalation. It supports multi-conversation (threaded) memory.

## 2) Prerequisites
- Windows 10/11
- Python 3.12+
- AI Router API key and OpenAI-compatible base URL

## 3) Setup
```powershell
# Create and activate venv
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Environment
Set-Content -Path .env -Value @(
  "AIROUTER_API_KEY=REPLACE_ME"
  "AIROUTER_BASE_URL=https://api.airouter.in/v1"
)
```

## 4) Project Structure
```text
project/
  agents/
    kb_agent.py               # HR/IT RAG agent
    ticket_creation_agent.py  # Escalation agent
    ticket_status_agent.py    # Ticket status by ID/email; sets last_ticket_id
  documents/                  # KB sources used by RAG
    hr-policies.md, it-support.md, onboarding.md, payroll.md
  ragSetup/
    rag_setup.py              # Build embeddings, vector store, retriever
  tickets/
    synthetic_tickets.json    # Mock ticket dataset (shown as source "tickets.db")
  smart_desk_ai_agent.py      # Graph assembly, state, routing, checkpointer, ask()

ui_smart_desk_ai_agent.py      # Gradio UI (Question + Thread ID required)
test_smart_desk_ai_agent.py    # Script harness with (query, thread_id) tuples
QuickStart.md                   # One-page setup
Architecture.md                 # Diagrams and data flow
```

## 5) RAG Pipeline (project/ragSetup/rag_setup.py)
- Loads markdown documents.
- Splits with RecursiveCharacterTextSplitter.
- Embeds via OpenAIEmbeddings through the configured AI Router endpoint using `openai/text-embedding-3-small`, then stores in Chroma.
- Exposes `retriever` (k configurable; MMR optional) and `format_docs`.
- AI Router model IDs use the provider-qualified `provider/model` form (for example, `openai/gpt-4o-mini`).

## 6) Core Agent Graph (project/smart_desk_ai_agent.py)
- SupportState fields:
  - `query`, `intent`, `response`, `context`, `retrieved_sources`, `history`, `effective_query`, `last_ticket_id`.
- Nodes in LangGraph:
  - `rewrite_query` — resolves anaphora (e.g., “that ticket”) using `last_ticket_id`.
  - `classify_intent` — routes to `kb_query`, `tkct_status`, or `tkct_creation`.
  - `kb_query_agent` — RAG over documents (sources are the markdown filenames).
  - `ticket_status_agent` — lookup by ID/email; sets `last_ticket_id`; sources shown as `tickets.db`.
  - `ticket_creation_agent` — collects details and provides escalation channels.
- Checkpointer:
  - Default: `MemorySaver` (in-process).
  - Optional: `SqliteSaver` for durable memory (install `langgraph-checkpoint-sqlite`).
- `ask(app, query, thread_id)`:
  - Only sends `{ "query": ... }` so persisted state is preserved per `thread_id`.

## 7) UI (ui_smart_desk_ai_agent.py)
- Gradio interface with required fields:
  - Your question (required)
  - Thread ID (required)
- On submit, calls `ask(app, query, thread_id)` and displays Response, Detected intent, Retrieved sources.

## 8) Test Harness (test_smart_desk_ai_agent.py)
- `TEST_QUERIES` supports either a string or a `(query, thread_id)` tuple.
- Use the same `thread_id` to demonstrate multi-conversation memory and query-rewrite:
```python
# python
TEST_QUERIES = {
  "Q1 — Thread B": ("Give me the status for Ticket created for marry.smith@gmail.com", "cust-B"),
  "Q2 — Thread B": ("Give me the description and priority for that Ticket", "cust-B"),
}
```

## 9) Retrieval Tuning
- Build with higher recall and reranking:
```python
# python
agent = build_support_agent(top_k=3, enable_reranking=True, rerank_fetch_k=6)
```
- Optional MMR in `rag_setup.py`:
```python
# python
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": top_k, "lambda_mult": 0.4})
```

## 10) Run
```powershell
# UI
python ui_smart_desk_ai_agent.py

# Script
python test_smart_desk_ai_agent.py
```

## 11) Troubleshooting
- Set `AIROUTER_API_KEY` and `AIROUTER_BASE_URL` in the repository-root `.env`.
- Use `from langgraph.checkpoint.memory import MemorySaver`.
- Keep the same Thread ID for follow-ups.
- If documents change, consider rebuilding the vector store (new `collection_name`).

---
