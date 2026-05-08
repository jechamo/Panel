# Panel — visual editor for LLM agents and HTTP microservices

A mini-n8n style canvas where you drag, connect and run two kinds of nodes:

- **Agent** — a Python-side LLM call with system/user prompts, file attachments
  (PDF / DOCX / XLSX) parsed into context, and a user-defined JSON output schema.
- **Microservice** — a configurable HTTP request (method, URL, headers, body)
  whose JSON response feeds the next node.

Outputs flow downstream: any node's JSON can be referenced from a downstream
node's prompt or request body using `{{node_id.field}}` placeholders.

## Stack

- **Backend**: FastAPI + SQLite (flows, settings) + Fernet-encrypted API keys
- **Frontend**: React + Vite + React Flow + Zustand
- **LLM providers**: Anthropic, OpenAI, Google Gemini, GitHub Models

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The frontend talks to the backend on port 8000.

### 3. Configure providers

Open the **Settings** panel (gear icon) and paste at least one API key
(Anthropic, OpenAI, Gemini, or a GitHub PAT for GitHub Models). Keys are
encrypted on disk with a master key auto-generated on first run.

## Layout

```
backend/
  app/
    main.py                FastAPI entry point
    db.py                  SQLite + SQLAlchemy
    crypto.py              Fernet encryption for secrets
    models.py              ORM: Flow, Setting
    schemas.py             Pydantic request/response shapes
    api/                   HTTP routes
    llm/                   Provider clients (Anthropic, OpenAI, Gemini, GH Models)
    parsers/               PDF, DOCX, XLSX text extraction
    runners/               Graph topological runner + per-node executors
frontend/
  src/
    components/
      Canvas.tsx           React Flow canvas
      Toolbar.tsx          Run all / Save / New
      nodes/               Visual node components
      panels/              Right-side config panels + Settings
    store/flow.ts          Zustand store
    api/client.ts          Backend client
```

## Running a flow

- **Run all** — topological order; each node receives `{ <upstream_id>: <output> }`.
- **Run node** — only that node, using whatever its parents last produced.
