"""Sales question to SQL to answer. LAB APP: never deploy it.

Phase 6 fixes from the CS54 remediation plan:
  PB-09 the generated SQL runs as one statement, on a read-only connection, under an authorizer
        that allows SELECT only; anything else is refused, not run
  PB-10 the own-region rule is enforced by the database: the model can query only a view of the
        employee's own region, and the salaries table is denied whatever the model writes
"""
import sqlite3
from pathlib import Path

from app import db, llm

SYSTEM = (Path(__file__).resolve().parent.parent / "prompts" / "system.txt").read_text()
MAX_ROWS = 200
REFUSAL = "I can only answer read-only questions about your own region's orders."


def _scope(conn: sqlite3.Connection, region: str) -> None:
    """A per-session view of the employee's own region. The region comes from the sign-in, never the model."""
    if region not in set(db.USERS.values()):
        raise PermissionError("unknown employee")
    conn.execute("DROP VIEW IF EXISTS temp.my_orders")
    conn.execute(f"CREATE TEMP VIEW my_orders AS SELECT id, region, customer, product, amount, order_date "
                 f"FROM main.orders WHERE region = '{region}'")  # region is from the allow-list above


def _authorizer(action, table, column, database, source):
    if action == sqlite3.SQLITE_SELECT or action == sqlite3.SQLITE_FUNCTION:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ and (
            (table == "my_orders" and database == "temp") or (table == "orders" and source == "my_orders")):
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def ask(question: str, user: str, conn=None) -> dict:
    conn = conn or db.connect()
    _scope(conn, db.USERS.get(user, "unknown"))
    sql = llm.to_sql(SYSTEM, f"Employee {user} asks: {question}").strip().rstrip(";")
    conn.set_authorizer(_authorizer)
    try:
        cur = conn.execute(sql)  # one statement only: sqlite3 refuses a second one
        rows = cur.fetchmany(MAX_ROWS)
        cols = [d[0] for d in cur.description] if cur.description else []
    except sqlite3.Error:
        return {"sql": sql, "columns": [], "rows": [], "refused": True, "answer": REFUSAL}
    finally:
        conn.set_authorizer(None)
    return {"sql": sql, "columns": cols if rows else [], "rows": rows}
