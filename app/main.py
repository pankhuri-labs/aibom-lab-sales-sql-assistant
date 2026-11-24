"""HTTP API for the sales assistant (lab)."""
from fastapi import FastAPI

from app.assistant import ask

app = FastAPI(title="Sales SQL assistant (lab)")


@app.post("/ask")
def ask_endpoint(payload: dict) -> dict:
    return ask(str(payload.get("question", "")), str(payload.get("user", "")))
