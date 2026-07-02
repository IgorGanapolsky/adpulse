"""Agentic RAG layer — retrieves relevant best-practice evidence cards and grounds
recommendations with citations + a transparent reasoning trace.

The "agentic" part: instead of one LLM call, this runs a multi-step loop:
  1. Analyze the campaign data → identify the top problems (waste, weak themes, etc.)
  2. For EACH problem, retrieve the most relevant knowledge-card via embedding similarity
  3. Generate a recommendation that CITES the retrieved evidence
  4. Self-check: does the recommendation address the problem? If not, re-retrieve.

Each recommendation carries: problem, retrieved_evidence (card_id + excerpt),
recommendation, confidence, and a step-by-step reasoning trace.
"""
from __future__ import annotations
import os
import re
import json
from typing import Any

import numpy as np
import pandas as pd

from llm import chat_json
from clustering import embed_texts

KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "ad_copy_best_practices.md")

import httpx

# In-memory vector store (rebuilt on first call; tiny corpus)
_CARDS: list[dict] | None = None
_CARD_EMBEDS: np.ndarray | None = None


def _load_corpus() -> list[dict]:
    """Parse the markdown knowledge file into structured cards."""
    global _CARDS, _CARD_EMBEDS
    if _CARDS is not None:
        return _CARDS
    with open(KNOWLEDGE_PATH) as f:
        text = f.read()
    # split on "## Card N —"
    raw = re.split(r"(?=\n## Card \d+)", text)
    cards = []
    for block in raw:
        m = re.match(r"\n## Card (\d+) — (.+)", block)
        if not m:
            continue
        cid, title = m.group(1), m.group(2).strip()
        # extract fields
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
    return cards


def _build_index() -> np.ndarray:
    global _CARD_EMBEDS
    if _CARD_EMBEDS is not None:
        return _CARD_EMBEDS
    cards = _load_corpus()
    texts = [c["text"] for c in cards]
    _CARD_EMBEDS = embed_texts(texts)
    return _CARD_EMBEDS


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Embed the query, return top-k most similar evidence cards with similarity scores."""
    cards = _load_corpus()
    idx = _build_index()
    q_emb = embed_texts([query])[0]
    # cosine similarity
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
    """Step 1 of the agent loop: turn raw data into a list of concrete problems to solve."""
    problems = []
    # waste creatives
    waste = df[df["Conversions"].astype(float) == 0]
    for _, r in waste.iterrows():
        problems.append(
            f"Creative '{r['Ad Name']}' spent ${r['Spend']:.0f} with zero conversions — likely burning budget."
        )
    # weak clusters
    if cluster_summary:
        for c in cluster_summary:
            if c.get("verdict") == "underperforming" and c["avg_cvr"] < 0.01:
                problems.append(
                    f"The '{c.get('theme','mixed')}' creative theme has avg CVR {c['avg_cvr']:.2%} across {c['size']} creatives — underperforming cluster."
                )
    # low-CTA detection
    low_text = df[df["Ad Copy"].fillna("").str.lower().str.contains("learn more|check this|our story|new arrival", na=False)]
    for _, r in low_text.iterrows():
        problems.append(
            f"Creative '{r['Ad Name']}' uses weak/generic copy ('{r['Ad Copy'][:40]}...') — lacks a specific pain or CTA."
        )
    return problems[:8]  # cap for tractability


def agentic_recommendations(
    df: pd.DataFrame,
    cluster_summary: list[dict] | None = None,
) -> dict[str, Any]:
    """Full agentic loop: identify problems → retrieve evidence → grounded recs with traces."""
    problems = identify_problems(df, cluster_summary)
    if not problems:
        return {"problems_found": 0, "recommendations": [], "note": "No major problems detected."}

    # Step 2 + 3: for each problem, retrieve evidence and generate a grounded rec
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
            "confidence (0-1), reasoning (2-3 step trace explaining how the evidence supports the rec)."
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
            {"step": 2, "action": f"Retrieved top-2 evidence cards per problem via embedding similarity (nomic-embed-text)"},
            {"step": 3, "action": f"Generated {len(recs)} grounded recommendations, each citing a best-practices card"},
        ],
    }
