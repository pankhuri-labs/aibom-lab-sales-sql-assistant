"""The gateway backend sends an OpenAI-compatible request with this app's own key (CS54 phase 7)."""
import io
import json

from app import llm


def test_gateway_backend_sends_app_key_and_strips_fences(monkeypatch):
    sent = {}

    def fake_urlopen(req, timeout):
        sent.update(url=req.full_url, body=json.loads(req.data), auth=req.get_header("Authorization"))
        reply = {"choices": [{"message": {"content": "```sql\nSELECT COUNT(*) FROM my_orders\n```"}}]}
        return io.BytesIO(json.dumps(reply).encode())

    monkeypatch.setenv("LLM_BACKEND", "gateway")
    monkeypatch.setenv("GATEWAY_URL", "http://gw.test")
    monkeypatch.setenv("GATEWAY_KEY", "sk-lab-test")
    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    assert llm.to_sql("system", "How many orders?") == "SELECT COUNT(*) FROM my_orders"
    assert sent["url"] == "http://gw.test/chat/completions" and sent["auth"] == "Bearer sk-lab-test"
    assert sent["body"]["model"] == "gemma2:2b"
