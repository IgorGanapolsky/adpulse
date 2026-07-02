"""LLM client — supports OpenRouter (production) and Ollama (local dev).

Production uses OpenRouter for hosted model access without local GPU.
Local dev falls back to Ollama if OPENROUTER_API_KEY is not set.
"""
import json
import os
import httpx

# --- Provider selection ----------------------------------------------------
# If OPENROUTER_API_KEY is set, use OpenRouter (OpenAI-compatible API).
# Otherwise fall back to local Ollama for development.
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.environ.get("ADPULSE_MODEL", "meta-llama/llama-3.3-70b-instruct")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("ADPULSE_OLLAMA_MODEL", "qwen3:14b")
FALLBACK_OLLAMA_MODEL = "qwen2.5-coder:14b"


def _chat_openrouter(prompt: str, *, json_mode: bool, temperature: float) -> str:
    """Call OpenRouter (OpenAI-compatible)."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 1200,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    r = httpx.post(
        f"{OPENROUTER_BASE}/chat/completions",
        headers=headers,
        json=payload,
        timeout=120.0,
    )
    r.raise_for_status()
    data = r.json()
    content = data["choices"][0]["message"]["content"].strip()
    return content


def _chat_ollama(prompt: str, *, json_mode: bool, temperature: float) -> str:
    """Call local Ollama."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 1200},
    }
    if json_mode:
        payload["format"] = "json"

    last_err = None
    for model in (OLLAMA_MODEL, FALLBACK_OLLAMA_MODEL):
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


def chat(prompt: str, *, json_mode: bool = False, temperature: float = 0.4, retries: int = 1) -> str:
    """Call LLM and return text. Uses OpenRouter in production, Ollama locally."""
    if OPENROUTER_API_KEY:
        return _chat_openrouter(prompt, json_mode=json_mode, temperature=temperature)
    return _chat_ollama(prompt, json_mode=json_mode, temperature=temperature)


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
