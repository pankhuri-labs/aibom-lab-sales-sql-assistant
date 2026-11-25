# aibom-lab-sales-sql-assistant

Ask a sales question in plain English; the assistant writes a SQL query with **Gemma 2 2B** running locally on Ollama, runs it on a small synthetic sales database and returns the rows.

> **Deliberately vulnerable lab app. Never deploy it or point it at a real database.** It is one of four sample apps for the [CS54 AI-BOM and AI security posture lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). Its planted weaknesses are listed in [KNOWN-WEAKNESSES.md](KNOWN-WEAKNESSES.md), with the phase 6 fixes. All data is fake.

## What it is, in AI-BOM terms

| AI-BOM field | Value |
| --- | --- |
| Model | `gemma2:2b` (Google Gemma 2, 2B parameters) |
| Hosting | Local, Ollama on `localhost:11434` |
| Prompt | `prompts/system.txt` (holds the view's schema; the region rule is enforced by the database since phase 6) |
| Sources | Employee question (untrusted) |
| Sinks | SQLite database (one SELECT, read-only, under an authorizer), then JSON rows |
| Identity | Read-only database connection, own-region view |
| Autonomy | Acts alone: generated SQL runs without review |

## Run it on a Mac

1. Install Ollama: [ollama.com/download](https://ollama.com/download) or `brew install ollama`, and start it.
2. Pull the model (about 1.6 GB): `ollama pull gemma2:2b`
3. Python 3.11 or later:
   ```
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
4. Start the API: `uvicorn app.main:app --port 8003`. The database `sales.db` is created on first use.
5. Ask a question:
   ```
   curl -s localhost:8003/ask -H 'Content-Type: application/json' \
     -d '{"question": "What are total sales by region?", "user": "asha"}'
   ```

## Through the AI gateway (CS54 phase 7)

Set `LLM_BACKEND=gateway`, `GATEWAY_URL` and `GATEWAY_KEY` in your local `.env`. Every model call then goes through the lab's LiteLLM gateway, which checks this app's key, refuses any model its AI-BOM does not list, and writes a trace that the runtime monitor reads. The gateway and how to start it are in the CaseStudies repository, under `CS54-AI-BOM-and-AI-Security-Posture-Lab/gateway/`. The gateway key is made by that folder's `build_config.py`; keep it only in `.env`.

## Tests

The tests use a scripted fake model, so they need no Ollama:

```
LLM_BACKEND=fake python -m pytest -q
```

The attack tests in `tests/test_attacks.py` assert the safe behaviour. In phase 3 they were expected failures, because the weaknesses were planted. Phase 6 fixed them, so they now pass and prove each fix holds. To see the attacks succeed, check out the last commit before the phase 6 fix PR and run `python -m pytest -q --runxfail tests/test_attacks.py`.

