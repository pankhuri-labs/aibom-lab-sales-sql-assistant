"""Sales question to SQL to answer. DELIBERATELY VULNERABLE LAB APP: never deploy it."""
from pathlib import Path

from app import db, llm

SYSTEM = (Path(__file__).resolve().parent.parent / "prompts" / "system.txt").read_text()


def ask(question: str, user: str, conn=None) -> dict:
    conn = conn or db.connect()
    region = db.USERS.get(user, "unknown")
    # Weakness AT-10: the region rule lives only in the prompt; the database does not enforce it.
    sql = llm.to_sql(SYSTEM, f"Employee {user} (region {region}) asks: {question}")
    # Weakness AT-09: model output runs as SQL with no parsing or allow-list; several statements allowed.
    rows = []
    for statement in [s for s in sql.split(";") if s.strip()]:
        cur = conn.execute(statement)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
    return {"sql": sql, "columns": cols if rows else [], "rows": rows}
