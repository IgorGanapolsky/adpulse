"""Creative clustering — embed ad copy, group into thematic clusters, and
report which themes convert and which burn budget.

Uses Ollama nomic-embed-text (768-dim) for embeddings and k-means for clustering.
This surfaces insights that raw CPA sorting misses: e.g. 'all your urgency/discount
creives underperform' vs 'your social-proof cluster is your goldmine'.
"""
from __future__ import annotations
import os
import json
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from llm import chat_json

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
EMBED_MODEL = os.environ.get("ADPULSE_EMBED_MODEL", "nomic-embed-text")

import httpx


def embed_texts(texts: list[str]) -> np.ndarray:
    """Batch-embed via Ollama. Returns (N, 768) array."""
    out = []
    # Ollama embed endpoint accepts a batch under "input"
    for i in range(0, len(texts), 32):
        batch = texts[i : i + 32]
        r = httpx.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": batch},
            timeout=60.0,
        )
        r.raise_for_status()
        out.extend(r.json()["embeddings"])
    return np.array(out, dtype=float)


def cluster_creatives(df: pd.DataFrame) -> dict[str, Any]:
    """Embed copy, cluster with k-means (auto-k), and summarize each cluster.

    Returns cluster themes with aggregate performance so the user sees which
    creative *themes* work, not just which individual ads work.
    """
    copies = df["Ad Copy"].fillna("").astype(str).tolist()
    if not any(c.strip() for c in copies):
        return {"error": "No ad copy found to cluster."}

    emb = embed_texts(copies)

    # auto-select k: min 2, max sqrt(N), prefer silhouette-ish heuristic via inertia elbow
    n = len(df)
    k_max = max(2, min(6, int(np.sqrt(n))))
    if n < 4:
        k = min(2, n)
    else:
        # simple elbow: try 2..k_max, pick k with best inertia drop ratio
        best_k, best_score = 2, -1
        inertias = {}
        for k_try in range(2, k_max + 1):
            km = KMeans(n_clusters=k_try, n_init=10, random_state=42).fit(emb)
            inertias[k_try] = km.inertia_
        # pick the k where the relative drop from k-1 -> k is largest
        for k_try in range(3, k_max + 1):
            drop = (inertias.get(k_try - 1, 0) - inertias[k_try]) / max(inertias.get(k_try - 1, 1), 1e-9)
            if drop > best_score:
                best_score, best_k = drop, k_try
        k = best_k

    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(emb)
    labels = km.labels_

    # aggregate per-cluster performance
    df = df.copy()
    df["_cluster"] = labels
    df["_cvr"] = df["Conversions"].astype(float) / df["Clicks"].clip(lower=1).astype(float)
    df["_cpa"] = df["Spend"].astype(float) / df["Conversions"].clip(lower=1).astype(float)

    clusters = []
    for cid in sorted(set(labels)):
        members = df[df["_cluster"] == cid]
        total_spend = float(members["Spend"].sum())
        total_conv = int(members["Conversions"].sum())
        avg_cvr = float(members["_cvr"].mean())
        avg_cpa = float(members["_cpa"].replace([np.inf, -np.inf], np.nan).mean() or 0)
        examples = members["Ad Copy"].fillna("").astype(str).head(3).tolist()
        clusters.append({
            "cluster_id": int(cid),
            "size": int(len(members)),
            "total_spend": round(total_spend, 2),
            "total_conversions": total_conv,
            "avg_cvr": round(avg_cvr, 4),
            "avg_cpa": round(avg_cpa, 2),
            "sample_copy": examples,
        })

    # rank clusters by efficiency (conversions per dollar)
    clusters.sort(key=lambda c: c["total_conversions"] / max(c["total_spend"], 1), reverse=True)
    for rank, c in enumerate(clusters):
        c["rank"] = rank + 1
        c["verdict"] = "goldmine" if rank < max(1, len(clusters) // 2) else "underperforming"

    # ask the LLM to name each cluster's theme from its sample copy
    named = _name_clusters(clusters)

    return {"k": k, "clusters": named, "embedding_dims": int(emb.shape[1])}


def _name_clusters(clusters: list[dict]) -> list[dict]:
    """LLM labels each cluster's creative theme from sample copy."""
    payload = [{"cluster_id": c["cluster_id"], "samples": c["sample_copy"]} for c in clusters]
    prompt = (
        "You are a direct-response marketing analyst. For each creative cluster below, "
        "infer the common creative THEME in 2-4 words (e.g. 'urgency/discount', 'social proof', "
        "'founder story', 'product feature'). Return ONLY a JSON object mapping cluster_id (as string) "
        "to a short theme label.\n\n"
        + json.dumps(payload)
    )
    try:
        labels = chat_json(prompt)
        if isinstance(labels, dict):
            for c in clusters:
                c["theme"] = labels.get(str(c["cluster_id"]), "mixed")
    except Exception:
        for c in clusters:
            c["theme"] = "mixed"
    return clusters
