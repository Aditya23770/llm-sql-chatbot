# Data-Whisperer — LLM SQL Chatbot

Ask questions about your data in plain English. The app converts natural language into PostgreSQL queries using an LLM, executes them, and returns results.

---

## Architecture

```
User (Streamlit UI)
  └── POST /query ──► FastAPI backend (Render)
                          ├── Redis (Upstash) — query result cache
                          ├── ChromaDB (in-process) — RAG schema retrieval
                          ├── LLM (Groq / OpenAI / Anthropic) — SQL generation
                          └── PostgreSQL (Neon) — query execution
```

**Request flow:**
1. Check Redis cache (cache key = SHA256 of provider + query) — return immediately on hit
2. ChromaDB semantic search → retrieve relevant column descriptions
3. Build prompt: full schema + RAG columns + user query → LLM → raw SQL
4. Execute SQL on PostgreSQL → return results + cache them

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11, Uvicorn |
| Frontend | Streamlit |
| Database | PostgreSQL (Neon.tech) |
| Cache | Redis (Upstash) |
| RAG / Vector store | ChromaDB + sentence-transformers (all-MiniLM-L6-v2) |
| LLM providers | Groq (llama3-8b-8192), OpenAI (gpt-4o), Anthropic (claude-sonnet-4-6) |

---

## Project Structure

```
llm-sql-chatbot/
├── app/                    # FastAPI backend
│   ├── api/routes/         # HTTP endpoints (health, query, admin)
│   ├── clients/            # LLM, database, and cache adapters
│   ├── core/               # Config, security, logging
│   ├── models/             # Pydantic request/response schemas
│   ├── prompts/            # SQL generation prompt template
│   └── services/           # Business logic: query handler, RAG, SQL extractor
├── ui/                     # Streamlit frontend
├── rag/                    # schema_definitions.json (RAG source of truth)
├── requirements.txt        # Backend dependencies
├── render.yaml             # Render deploy config
└── .env.example            # Environment variable template
```

---

## Local Setup

### 1. Clone and install

```bash
git clone https://github.com/Aditya23770/llm-sql-chatbot
cd llm-sql-chatbot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your keys in .env
```

Required env vars (see `.env.example` for all options):
- `GROQ_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`
- `DB_URL` — `postgresql+asyncpg://user:pass@host/db`
- `REDIS_URL` — `redis://localhost:6379` or Upstash `rediss://...`
- `API_KEY` — any secret string to protect the endpoints

### 3. Run the backend

```bash
uvicorn app.main:app --reload
# http://localhost:8000
```

ChromaDB schema ingestion runs automatically on first startup.

### 4. Run the frontend

```bash
BACKEND_URL=http://localhost:8000 API_KEY=your_key streamlit run ui/app.py
# http://localhost:8501
```

---

## API

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | — | Liveness check |
| POST | `/query` | `X-API-Key` | Natural language → SQL → results |
| POST | `/admin/reload-schema` | `X-API-Key` | Force ChromaDB re-ingestion |

**POST /query** example:
```json
// Request
{ "query": "Show me all female customers from Mumbai", "provider": "groq" }

// Response
{ "sql_query": "SELECT * FROM customers WHERE gender ILIKE 'female' AND location ILIKE 'mumbai';",
  "results": [...], "cached": false, "provider": "groq" }
```

---

## Deployment

| Service | Purpose | Free tier |
|---|---|---|
| Render.com | FastAPI backend | 512MB, auto-deploys from GitHub |
| Streamlit Community Cloud | Streamlit UI | Free, points to `ui/app.py` |
| Neon.tech | PostgreSQL | 0.5GB serverless Postgres |
| Upstash | Redis cache | 10k commands/day |
