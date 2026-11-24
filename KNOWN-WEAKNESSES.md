# Known weaknesses (planted on purpose)

This app is a target for the [CS54 AI-BOM security lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). IDs match the CS54 [threat model](https://github.com/pankhuri-labs/CaseStudies/blob/main/CS54-AI-BOM-and-AI-Security-Posture-Lab/docs/threat-model.md). Attack tests arrive in phase 3 and fixes in phase 6.

| ID | Weakness | Where | OWASP LLM 2025 |
| --- | --- | --- | --- |
| AT-09 | Model output runs as SQL with no parsing or allow-list, on a read-write connection, and several statements are allowed | `app/assistant.py` `ask()`, `app/db.py` `connect()` | LLM05, LLM06 |
| AT-10 | The "own region only" rule lives only in the prompt; the database does not enforce it, and the restricted salaries table is reachable | `prompts/system.txt`, `app/assistant.py` | LLM02 |
