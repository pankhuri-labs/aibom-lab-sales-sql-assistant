"""Creates a small synthetic sales database. All data is fake."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "sales.db"

ORDERS = [
    (1, "North", "Customer N1", "Widget", 1200.0, "2026-10-01"),
    (2, "North", "Customer N2", "Gadget", 800.0, "2026-10-03"),
    (3, "South", "Customer S1", "Widget", 1500.0, "2026-10-04"),
    (4, "South", "Customer S2", "Gizmo", 300.0, "2026-10-07"),
    (5, "West", "Customer W1", "Gadget", 950.0, "2026-10-09"),
]
SALARIES = [("Rep North", "North", 52000.0), ("Rep South", "South", 54000.0), ("Rep West", "West", 50000.0)]
USERS = {"asha": "North", "ravi": "South"}  # employee -> region they may see


def reset(path: Path | None = None) -> sqlite3.Connection:
    path = path or DB_PATH
    path.unlink(missing_ok=True)
    conn = sqlite3.connect(path, isolation_level=None)
    conn.execute("CREATE TABLE orders(id INTEGER, region TEXT, customer TEXT, product TEXT, amount REAL, order_date TEXT)")
    conn.execute("CREATE TABLE salaries(employee TEXT, region TEXT, salary REAL)")
    conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", ORDERS)
    conn.executemany("INSERT INTO salaries VALUES (?,?,?)", SALARIES)
    return conn


def connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or DB_PATH
    if not path.exists():
        reset(path).close()  # create the sample data, then reopen read-only like every other run
    # Phase 6 (PB-09): the assistant only ever reads, so it opens the database read-only.
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True, isolation_level=None)
