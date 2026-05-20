# Backend — Mission Authoring Pure-Logic Service

Pure-logic FastAPI server. KEINE LLM-Calls hier (die laufen in Claude Code Subagents). Backend ist für:

- Asset-Catalog Validation
- Mission-File Generation (Reforger-Bridge)
- Snapshot-Storage
- Schema-Validation

## Setup (macOS)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --port 8765 --reload
```

Health Check: `curl http://localhost:8765/health` → `{"status":"ok",...}`

## Architecture

```
backend/
├── main.py                # FastAPI Entry
├── requirements.txt
├── llm/                   # Provider-Abstraction (geplant — siehe DECISIONS.md)
│   └── __init__.py
├── catalog/               # Asset-Catalog Logic
│   └── __init__.py
├── exporters/             # Mission-File Generators (Reforger-Bridge)
│   └── __init__.py
├── snapshots/             # Snapshot-DB Logic
│   └── __init__.py
└── tests/                 # PyTest
```

## Provider-Abstraction

Auch wenn aktuell nur Claude genutzt wird (siehe DECISIONS.md 2026-05-20), ist das LLM-Interface abstrahiert:

```python
from llm.interface import LLMProvider

provider = LLMProvider.get("claude")  # später: "openai", "gemini"
```

## Sonnet 4.6 TODO

Die Module unter `routes/`, `llm/`, `catalog/`, `exporters/`, `snapshots/` werden basierend auf `research/02-mission-format.md` und `research/00-synthesis.md` instantiiert. Siehe `EXECUTION_PROMPT_FOR_SONNET_4_6.md`.
