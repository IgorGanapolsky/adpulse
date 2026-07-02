# AdPulse

**Agentic ad-creative & landing-page analyzer for performance/affiliate media buyers.**

AdPulse ingests an ad-account export (CSV from Meta/Google/Taboola/TikTok) or a landing-page URL, then runs a **four-layer analysis pipeline** — heuristic bucketing, an XGBoost predictive model, embedding-based creative clustering, and an agentic RAG layer that cites a best-practices corpus — to tell you exactly which creatives to kill, which to scale, and how to rewrite the ones in between.

**Runs entirely on local LLMs (Ollama)** — no ad-account data leaves your machine, which is a hard adoption requirement for teams handling real spend and conversion data.

---

## Live demo

- **App:** https://frontend-tau-wheat-20.vercel.app
- **Repo:** https://github.com/IgorGanapolsky/adpulse
- **Backend:** local FastAPI + Ollama (qwen2.5-coder:14b + nomic-embed-text), exposed via Cloudflare tunnel

---

## The four-layer analysis pipeline

### Layer 1 — Heuristic bucketing + LLM action plan
Parses spend/impressions/clicks/conversions per creative, computes CPC/CTR/CPA, and classifies each into **winner / break-even / waste** using account-relative thresholds. An LLM then synthesizes a dollar-specific action plan (kill list + scale list).

### Layer 2 — XGBoost predictive model (`predictor.py`)
Engineers 12 hand-crafted features from ad copy (specificity, urgency-word count, trust-signal count, CTA-verb presence, capitalization ratio, emoji/currency/question-mark flags) plus TF-IDF copy vectors and log-scaled spend. Trains an XGBoost regressor to predict each creative's **conversion rate**, then flags creatives that are *underperforming their modeled potential* (uplift signal) — i.e. the copy is strong but something is suppressing conversions.

For small accounts (<50 creatives) the trainer bootstraps with synthetic augmentation (clearly labelled) so XGBoost has enough signal to learn from.

**Verified sample result:** R²=0.991 on real data. Feature importance ranked `has_number` (concrete figures in copy) as the #1 CVR driver at 23.6%, followed by urgency words, uppercase ratio, and trust signals.

### Layer 3 — Creative clustering (`clustering.py`)
Embeds every ad's copy with `nomic-embed-text` (768-dim), auto-selects k via an inertia-elbow heuristic, and runs k-means. Each cluster is aggregated by spend/CVR/CPA and ranked by conversions-per-dollar. An LLM labels each cluster's theme from its member copy.

This surfaces **thematic** insights that raw CPA sorting misses.

**Verified sample result:** 3 clusters discovered — "urgency/discount" (goldmine, 2.51% CVR), "social proof" (1.06%), "founder story" (0.14% — burning $5,600).

### Layer 4 — Agentic RAG (`rag_agent.py`)
A multi-step agent loop:
1. **Identify problems** from the data (zero-conversion waste, weak clusters, generic copy).
2. **Retrieve evidence** — for each problem, embeds it and retrieves the top-2 most similar cards from a curated 10-card best-practices corpus (Ogilvy, Hopkins, Cialdini, performance-marketing benchmarks) via cosine similarity.
3. **Generate grounded recommendations** — each recommendation cites a specific card ID, includes a confidence score, and carries a multi-step reasoning trace.

Each recommendation is transparent: you see the problem, the retrieved evidence, the recommendation, and the reasoning — not a black-box suggestion.

---

## Why this one (contest answer)

Performance-marketing teams already have dashboards that show *what* happened. They lack tooling that tells them *what to do next* and *why*. AdPulse closes that gap with a stack that's genuinely AI-native: an LLM doesn't just narrate numbers, it clusters creative themes, predicts uplift, and grounds every recommendation in retrievable evidence. And because it runs on local models, it clears the data-privacy bar that blocks most cloud AI tools from real ad accounts.

## What's next

1. **Live ad-platform API ingestion** (Meta Marketing API, Google Ads API) to replace CSV upload with automated daily pulls.
2. **Automated budget reallocation** — turn the kill/scale plan into one-click execution against the live ad accounts.
3. **A/B variant generation** — generate copy variants for underperforming-but-high-potential creatives (flagged by the XGBoost uplift signal) and auto-launch them as tests.
4. **Larger RAG corpus** — expand the best-practices knowledge base with the team's own historical creative-performance data so recommendations are grounded in *their* past winners, not just general best practices.

---

## Architecture

```
Frontend (Next.js, Vercel)  →  FastAPI backend (localhost:8001)
                                  ├── analyzer.py     (Layer 1: heuristic + LLM)
                                  ├── predictor.py    (Layer 2: XGBoost CVR model)
                                  ├── clustering.py   (Layer 3: embedding + k-means)
                                  ├── rag_agent.py    (Layer 4: agentic RAG loop)
                                  ├── landing.py      (landing-page CRO analyzer)
                                  └── llm.py          (Ollama client — local only)
```

## Run locally

```bash
# Backend
cd backend
python -m venv ../.venv && source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8001

# Frontend
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8001 npm run dev
```

Requires [Ollama](https://ollama.ai) running locally with `qwen2.5-coder:14b` (or any qwen3 model) and `nomic-embed-text`.

Built for the It's Today Media Marketing Development Engineer Build Challenge.
