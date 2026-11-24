"""Functional tests with the fake model. Attack tests arrive in phase 3."""
from app import db
from app.assistant import ask


def test_total_sales_by_region(tmp_path):
    conn = db.reset(tmp_path / "t.db")
    out = ask("What are total sales by region?", "asha", conn)
    assert dict(out["rows"])["South"] == 1800.0


def test_orders_for_a_region(tmp_path):
    conn = db.reset(tmp_path / "t.db")
    out = ask("Show orders for region north", "asha", conn)
    assert len(out["rows"]) == 2


def test_api_answers(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from app import main

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    r = TestClient(main.app).post("/ask", json={"question": "How many orders?", "user": "ravi"})
    assert r.json()["rows"] == [[5]]
