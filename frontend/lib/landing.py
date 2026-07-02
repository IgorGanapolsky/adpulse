"""Landing-page analyzer — fetch a URL, extract copy/structure, and produce
high-impact rewrite recommendations via the local LLM."""
from __future__ import annotations
import re
import httpx
from bs4 import BeautifulSoup
from llm import chat_json


def fetch_page(url: str) -> dict:
    """Fetch a landing page and extract the text a marketer cares about."""
    if not url.startswith("http"):
        url = "https://" + url
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"}
    r = httpx.get(url, headers=headers, timeout=20.0, follow_redirects=True)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    def texts(selector):
        return [re.sub(r"\s+", " ", t.get_text(" ").strip())
                for t in soup.select(selector)
                if t.get_text(strip=True)]

    return {
        "url": url,
        "title": (soup.title.get_text(strip=True) if soup.title else "")[:200],
        "h1": texts("h1")[:3],
        "h2": texts("h2")[:6],
        "headlines": texts("h1, h2")[:8],
        "cta_buttons": list({t.get_text(strip=True) for t in soup.select("a, button")
                             if t.get_text(strip=True) and len(t.get_text(strip=True)) < 40})[:8],
        "body_paragraphs": [p for p in texts("p") if len(p) > 40][:12],
        "meta_description": (soup.find("meta", attrs={"name": "description"}) or {}).get("content", "") if soup.find("meta", attrs={"name": "description"}) else "",
    }


def analyze_landing_page(url: str) -> dict:
    """Full pipeline: fetch + LLM recommendations."""
    page = fetch_page(url)
    # Trim to fit context
    page_summary = {
        "url": page["url"],
        "title": page["title"],
        "h1": page["h1"],
        "cta_buttons": page["cta_buttons"],
        "first_paragraphs": page["body_paragraphs"][:5],
        "meta_description": page["meta_description"],
    }
    prompt = (
        "You are a senior conversion-rate-optimization expert reviewing a "
        "landing page for a performance-marketing team. Here is the page content:\n\n"
        f"{page_summary}\n\n"
        "Produce actionable recommendations. Return JSON:\n"
        '{\n'
        '  "score": 1-10,\n'
        '  "headline_feedback": {"current": "...", "issue": "...", "rewrite": "..."},\n'
        '  "cta_feedback": {"current": [...], "issue": "...", "rewrites": [...]},\n'
        '  "top_3_fixes": [{"fix": "...", "expected_impact": "...", "reasoning": "..."}],\n'
        '  "summary": "2 sentence executive summary"\n'
        "}"
    )
    recs = chat_json(prompt)
    return {"page": page, "recommendations": recs}
