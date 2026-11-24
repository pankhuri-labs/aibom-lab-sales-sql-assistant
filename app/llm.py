"""Model client. Ollama by default; a scripted fake model for tests (LLM_BACKEND=fake)."""
import json
import os
import re
import urllib.request


def to_sql(system: str, question: str) -> str:
    if os.environ.get("LLM_BACKEND", "ollama") == "fake":
        return _fake_model(question)
    payload = {"model": os.environ.get("SQL_MODEL", "gemma2:2b"),
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": question}],
               "stream": False, "options": {"temperature": 0}}
    req = urllib.request.Request(f"{os.environ.get('OLLAMA_URL', 'http://localhost:11434')}/api/chat",
                                 data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        text = json.loads(resp.read())["message"]["content"]
    return re.sub(r"^```(?:sql)?|```$", "", text.strip(), flags=re.M).strip()


def _fake_model(question: str) -> str:
    """A compliant model with no defences: writes whatever SQL the question asks for."""
    question = question.split("asks:", 1)[-1]
    q = question.lower()
    asked = re.search(r"run this sql:\s*(.+)", question, re.I | re.S)
    if asked:
        return asked.group(1).strip()
    region = re.search(r"region (\w+)", q)
    if "total" in q and "region" in q:
        return "SELECT region, SUM(amount) AS total FROM orders GROUP BY region"
    if "salar" in q:
        return "SELECT employee, region, salary FROM salaries"
    if region:
        return f"SELECT * FROM orders WHERE region = '{region.group(1).title()}'"
    return "SELECT COUNT(*) AS orders FROM orders"
