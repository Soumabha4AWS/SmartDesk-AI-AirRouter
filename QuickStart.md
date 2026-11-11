# Smart Desk AI — Quick Start

This guide shows how to set up and run the Smart Desk AI app (UI and script) on Windows.

## 1) Prerequisites
- Windows 10/11
- Python 3.12+ (`py -V`)
- AI Router API key and OpenAI-compatible base URL

## 2) Create and activate a virtual environment
```powershell
# From the repository root
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 3) Install dependencies
```powershell
pip install -U langchain langchain-openai langchain-chroma langgraph gradio python-dotenv
# Optional (durable thread memory via SQLite)
pip install -U langgraph-checkpoint-sqlite
```

## 4) Configure environment
```powershell
# Create a .env file in the repo root with your AI Router credentials
Set-Content -Path .env -Value @(
  "AIROUTER_API_KEY=REPLACE_ME"
  "AIROUTER_BASE_URL=https://api.airouter.in/v1"
)
```

## 5) Run the UI (Gradio)
```powershell
python ui_smart_desk_ai_agent.py
```
- Thread ID (required): use the same value (e.g., `cust-demo`) for follow‑ups to enable multi‑conversation memory.
- Examples:
  - "Give me the status for Ticket created for marry.smith@gmail.com"
  - then (same Thread ID): "Give me the description and priority for that Ticket"

## 6) Run the script tests
```powershell
python test_smart_desk_ai_agent.py
```
- The test harness supports tuples `(query, thread_id)` so you can group related questions under the same thread.

## 7) Retrieval quality options (optional)
You can increase recall and improve ranking when asking KB questions like "Code of conduct":
- In both UI and tests, build the agent with:
```python
# python
agent = build_support_agent(
    collection_name="smartdesk_demo",
    top_k=3,
    enable_reranking=True,
    rerank_fetch_k=6,
)
```
- (Alternative) Use MMR in `project/ragSetup/rag_setup.py`:
```python
# python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": top_k, "lambda_mult": 0.4},
)
```

## 8) Multi‑conversation memory
- The app persists per‑thread state using LangGraph’s checkpointer.
- Default: in‑memory (`MemorySaver`) — resets on process restart.
- Durable (optional): enable SQLite in `project/smart_desk_ai_agent.py` and install `langgraph-checkpoint-sqlite`.

```python
# python
# from langgraph.checkpoint.sqlite import SqliteSaver
# db_path = Path(__file__).parent / "data" / "conversations.db"
# db_path.parent.mkdir(parents=True, exist_ok=True)
# saver = SqliteSaver(str(db_path))
# app = graph.compile(checkpointer=saver)
```

## 9) Troubleshooting
- Missing AI Router configuration: ensure `.env` has `AIROUTER_API_KEY` and `AIROUTER_BASE_URL`, then restart.
- ImportError for MemorySaver: use `from langgraph.checkpoint.memory import MemorySaver`.
- Follow‑up not remembering the ticket: ensure the same Thread ID is set and you’re not reinitializing state (the included `ask()` only sends the new `query`).
- Sources show tickets.db for ticket answers from the synthetic dataset; KB answers show the specific Markdown file.

## 10) Project entry points
- UI: [ui_smart_desk_ai_agent.py](./ui_smart_desk_ai_agent.py)
- Script: [test_smart_desk_ai_agent.py](./test_smart_desk_ai_agent.py)
- Core agent: [project/smart_desk_ai_agent.py](./project/smart_desk_ai_agent.py)
