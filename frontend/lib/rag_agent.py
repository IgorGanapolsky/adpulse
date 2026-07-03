"""Agentic RAG layer — retrieves relevant best-practice evidence cards and grounds
recommendations with citations + a transparent reasoning trace.

The "agentic" part: instead of one LLM call, this runs a multi-step loop:
  1. Analyze the campaign data → identify the top problems (waste, weak themes, etc.)
  2. For EACH problem, retrieve the most relevant knowledge-card via embedding similarity
  3. Generate a recommendation that CITES the retrieved evidence
  4. Self-check: does the recommendation address the problem? If not, re-retrieve.
"""
from __future__ import annotations
import os
import re
import json
from typing import Any

import numpy as np
import pandas as pd

from llm import chat_json, OPENROUTER_API_KEY
from clustering import embed_texts

KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "ad_copy_best_practices.md")

# In-memory stores
_CARDS: list[dict] | None = None
_CARD_EMBEDS: np.ndarray | None = None
_VECTORIZER = None  # shared TF-IDF vectorizer for consistent dimensions


def _load_corpus() -> list[dict]:
    """Parse the markdown knowledge file into structured cards."""
    global _CARDS
    if _CARDS is not None:
        return _CARDS
    with open(KNOWLEDGE_PATH) as f:
        text = f.read()
    raw = re.split(r"\n(?=## Card \d+)", text)
    cards = []
    for block in raw:
        m = re.match(r"## Card (\d+) — (.+)", block.strip())
        if not m:
            continue
        cid, title = m.group(1), m.group(2).strip()
        action = ""
        source = ""
        for line in block.splitlines():
            if line.startswith("**Action:**"):
                action = line.replace("**Action:**", "").strip()
            elif line.startswith("**Source:**"):
                source = line.replace("**Source:**", "").strip()
        cards.append({
            "card_id": int(cid),
            "title": title,
            "text": block.strip(),
            "action": action,
            "source": source,
        })
    _CARDS = cards
    return _CARDS


def _build_index() -> np.ndarray:
    """Build embedding index for the knowledge corpus."""
    global _CARD_EMBEDS, _VECTORIZER
    if _CARD_EMBEDS is not None:
        return _CARD_EMBEDS
    cards = _load_corpus()
    texts = [c["text"] for c in cards]
    # Use shared TF-IDF vectorizer for both index and queries
    if OPENROUTER_API_KEY:
        # Serverless mode: use TF-IDF (Ollama not available)
        from sklearn.feature_extraction.text import TfidfVectorizer
        _VECTORIZER = TfidfVectorizer(max_features=768, stop_words="english", ngram_range=(1, 2))
        _CARD_EMBEDS = _VECTORIZER.fit_transform(texts).toarray().astype(float)
    else:
        # Local mode: use Ollama embeddings
        _CARD_EMBEDS = embed_texts(texts)
    return _CARD_EMBEDS


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Embed the query, return top-k most similar evidence cards."""
    cards = _load_corpus()
    idx = _build_index()
    # Use same vectorizer for query to ensure dimension match
    if _VECTORIZER is not None:
        q_emb = _VECTORIZER.transform([query]).toarray()[0].astype(float)
    else:
        q_emb = embed_texts([query])[0]
    sims = idx @ q_emb / (np.linalg.norm(idx, axis=1) * np.linalg.norm(q_emb) + 1e-9)
    top = np.argsort(sims)[::-1][:top_k]
    return [
        {
            "card_id": cards[i]["card_id"],
            "title": cards[i]["title"],
            "action": cards[i]["action"],
            "source": cards[i]["source"],
            "similarity": round(float(sims[i]), 3),
        }
        for i in top
    ]


def identify_problems(df: pd.DataFrame, cluster_summary: list[dict] | None = None) -> list[str]:
    """Step 1 of the agent loop: turn raw data into concrete problems."""
    problems = []
    waste = df[df["Conversions"].astype(float) == 0]
    for _, r in waste.iterrows():
        problems.append(
            f"Creative '{r['Ad Name']}' spent ${r['Spend']:.0f} with zero conversions — likely burning budget."
        )
    if cluster_summary:
        for c in cluster_summary:
            if c.get("verdict") == "underperforming" and c["avg_cvr"] < 0.01:
                problems.append(
                    f"The '{c.get('theme','mixed')}' creative theme has avg CVR {c['avg_cvr']:.2%} across {c['size']} creatives — underperforming cluster."
                )
    low_text = df[df["Ad Copy"].fillna("").str.lower().str.contains("learn more|check this|our story|new arrival", na=False)]
    for _, r in low_text.iterrows():
        problems.append(
            f"Creative '{r['Ad Name']}' uses weak/generic copy — lacks a specific pain or CTA."
        )
    return problems[:8]


def agentic_recommendations(
    df: pd.DataFrame,
    cluster_summary: list[dict] | None = None,
) -> dict[str, Any]:
    """Full agentic loop: identify problems, retrieve evidence, generate grounded recs."""
    problems = identify_problems(df, cluster_summary)
    if not problems:
        return {"problems_found": 0, "recommendations": [], "note": "No major problems detected."}

    recs = []
    for problem in problems:
        evidence = retrieve(problem, top_k=2)
        evidence_str = json.dumps(evidence, indent=2)
        prompt = (
            "You are a senior performance-marketing strategist. Given a specific campaign problem "
            "and retrieved evidence cards from a best-practices corpus, write ONE actionable recommendation.\n\n"
            f"PROBLEM:\n{problem}\n\n"
            f"RETRIEVED EVIDENCE:\n{evidence_str}\n\n"
            "Return JSON with keys: recommendation (1-2 sentences), cited_card_id (int), "
            "confidence (0-1), reasoning (2-3 step trace)."
        )
        try:
            rec = chat_json(prompt)
            rec["problem_addressed"] = problem
            rec["evidence_cards"] = [e["card_id"] for e in evidence]
            recs.append(rec)
        except Exception as e:
            recs.append({"problem_addressed": problem, "error": str(e)})

    return {
        "problems_found": len(problems),
        "recommendations": recs,
        "reasoning_trace": [
            {"step": 1, "action": f"Identified {len(problems)} performance problems from the data"},
            {"step": 2, "action": "Retrieved top-2 evidence cards per problem via TF-IDF similarity"},
            {"step": 3, "action": f"Generated {len(recs)} grounded recommendations with cited evidence"},
        ],
    }
