"""HTTP API for the sales assistant (lab)."""
from fastapi import FastAPI, HTTPException

from app.assistant import ask

app = FastAPI(title="Sales SQL assistant (lab)")


@app.post("/ask")
def ask_endpoint(payload: dict) -> dict:
    try:
        return ask(str(payload.get("question", "")), str(payload.get("user", "")))
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
