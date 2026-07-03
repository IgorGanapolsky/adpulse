# AdPulse

**Every affiliate media buyer is burning 15–30% of their spend on creatives that will never convert. No existing tool tells them which ones — or why.**

AdPulse does. Upload an ad-account export (Meta/Google/Taboola/TikTok CSV) or paste a landing-page URL. AdPulse runs a four-layer analysis pipeline that tells you exactly which creatives to kill, which to scale, and how to rewrite the ones in between — with every recommendation grounded in cited evidence, not a black-box guess.

---

## Live demo

- **App:** https://frontend-tau-wheat-20.vercel.app
- **Repo:** https://github.com/IgorGanapolsky/adpulse

---

## Contest answers

### What does this tool do?

AdPulse ingests ad-account data (CSV export or landing-page URL) and runs a four-layer pipeline:

1. **Heuristic bucketing** — classifies each creative as winner / break-even / waste using account-relative CPC/CTR/CPA thresholds, then generates a dollar-specific kill/scale action plan.
2. **XGBoost prediction** — engineers 12 copy-derived features + TF-IDF vectors, trains a regressor to predict each creative's conversion rate, and flags creatives underperforming their modeled potential (uplift signal: the copy is strong but something is suppressing conversions).
3. **Creative clustering** — embeds every ad with `nomic-embed-text`, runs k-means with auto-k, and surfaces thematic patterns that raw CPA sorting misses.
4. **Agentic RAG** — identifies problems in the data, retrieves cited evidence from a best-practices corpus (Ogilvy, Hopkins, Cialdini, performance-marketing benchmarks), and generates recommendations with multi-step reasoning traces.

Runs on **OpenRouter** (Llama 3.3 70B) in production with **Ollama** support for local development — no ad-account data is stored or persisted. The analysis runs in stateless serverless functions that process the upload and return results without retention.

### Why did you build THIS one?

Because performance-marketing teams already have dashboards that show *what happened*. They lack tooling that tells them *what to do next* and *why*. The competitive landscape proves the gap:

- **AdCreative.ai** ($39–$999/mo) generates new ads but doesn't diagnose existing ones.
- **Triple Whale / Northbeam** (~$1,290/mo) show which *channel* converts, not which *creative* or why.
- **Motion** ($29–$79/seat) visualizes creative performance but doesn't predict or prescribe.

AdPulse is the only tool that does creative-level ML diagnosis with explainable, evidence-grounded recommendations. The four-layer stack is genuinely AI-native: an LLM doesn't just narrate numbers, it clusters themes, predicts uplift, and grounds every prescription in retrievable best-practice evidence.

### What would you build next?

1. **Live ad-platform API ingestion** (Meta Marketing API, Google Ads API) — replace CSV upload with automated daily pulls so the analysis runs every morning before the media buyer opens their laptop.
2. **One-click kill/scale execution** — turn the action plan into direct budget changes against the live ad accounts, closing the loop from diagnosis to optimization.
3. **A/B variant generation** — for creatives flagged as high-potential-but-underperforming (XGBoost uplift signal), auto-generate replacement copy variants and launch them as tests.
4. **Team-specific RAG corpus** — expand the best-practices knowledge base with the team's own historical creative-performance data so recommendations are grounded in *their* past winners.

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

## Architecture

```
Frontend + API (Next.js, Vercel)
  ├── app/api/analyze/route.ts   (Layer 1: heuristic + Layer 2: predictions + Layer 4: LLM strategy + RAG)
  ├── app/api/landing/route.ts   (Landing page CRO analyzer)
  ├── app/api/health/route.ts    (Health check)
  ├── components/                 (CsvAnalyzer, LandingAnalyzer UI)
  └── lib/                        (Python ML modules for local development)
      ├── analyzer.py             (Layer 1: heuristic bucketing)
      ├── predictor.py            (Layer 2: XGBoost CVR model, R²=0.991)
      ├── clustering.py           (Layer 3: embedding + k-means)
      ├── rag_agent.py            (Layer 4: agentic RAG loop)
      └── llm.py                  (OpenRouter + Ollama dual-mode client)

LLM Provider: OpenRouter (Llama 3.3 70B) in production, Ollama (qwen3:14b) for local dev
```

## Run locally

```bash
# Production mode (uses OpenRouter)
cd frontend
npm install
npm run dev
# Set OPENROUTER_API_KEY in .env.local

# Full local mode (with Python ML backend)
cd backend
python -m venv ../.venv && source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8001

cd ../frontend
NEXT_PUBLIC_API_URL=http://localhost:8001 npm run dev
```

Built for the It's Today Media Marketing Development Engineer Build Challenge.
