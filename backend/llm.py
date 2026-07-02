"""Ollama local-LLM client. No external API keys, no data egress."""
import json
import os
import httpx

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
# Prefer qwen3 for reasoning; fall back to qwen2.5-coder which is widely pulled.
DEFAULT_MODEL = os.environ.get("ADPULSE_MODEL", "qwen3:14b")
FALLBACK_MODEL = "qwen2.5-coder:14b"


def chat(prompt: str, *, json_mode: bool = False, temperature: float = 0.4, retries: int = 1) -> str:
    """Call the local Ollama model and return the text response."""
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 1200},
    }
    if json_mode:
        payload["format"] = "json"

    last_err = None
    for model in (DEFAULT_MODEL, FALLBACK_MODEL):
        payload["model"] = model
        try:
            r = httpx.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120.0)
            r.raise_for_status()
            data = r.json()
            content = (data.get("message") or {}).get("content", "").strip()
            if content:
                return content
        except Exception as e:  # noqa: BLE001
            last_err = e
            continue
    raise RuntimeError(f"Ollama call failed: {last_err}")


def chat_json(prompt: str, temperature: float = 0.3) -> dict:
    """Call Ollama in JSON mode and parse the result. Falls back to extracting JSON."""
    raw = chat(prompt, json_mode=True, temperature=temperature)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Model sometimes wraps JSON in prose or code fences — extract it.
        import re
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Could not parse JSON from model response: {raw[:300]}")
