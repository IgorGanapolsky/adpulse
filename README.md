# AdPulse

**Agentic ad-creative & landing-page analyzer for performance/affiliate media buyers.**

AdPulse ingests an ad-account export (CSV from Meta/Google/Taboola/TikTok) or a landing-page URL, then uses a local LLM (Ollama — no data leaves your machine) to:

1. **Cluster creatives by performance** — winners, break-even, and wasted spend.
2. **Flag waste & scaling candidates** — concrete $ figures on what to kill and what to scale.
3. **Generate improved ad-copy variants** with a reasoning trace for each change.
4. **Rewrite landing-page sections** — paste a URL, get high-impact rewrite recommendations with the "why."

Built for the It's Today Media Build Challenge.

---

## What does this tool do?

AdPulse is an AI-powered media-buying copilot. It turns raw ad-performance data into decisions and next actions: which creatives to kill, which to scale, and rewritten copy you can ship today. It runs on a **local LLM (Ollama)** so no ad-account or landing-page data ever leaves your machine — a hard requirement for any marketing team handling spend and conversion data.

## Why did you build THIS one?

Every affiliate/performance team I've talked to loses hours every week staring at spreadsheets, trying to decide what to kill, what to scale, and how to rewrite underperforming creatives. The data is there; the *decision* is slow and manual. An LLM is uniquely good at (a) clustering noisy creative data and (b) generating on-brand copy variants with a reasoning trail. I picked the problem that sits directly on the revenue line — kill waste faster, scale winners faster — rather than a reporting dashboard that just restates numbers.

The local-model choice is deliberate: marketers will not pipe real ad-account data through a third-party API. Privacy-safe-by-default is the only architecture that gets adopted.

## What would you build next if this were your full-time job?

1. **Live ad-platform connectors** (Meta Marketing API, Google Ads API, TikTok Ads, Taboola) replacing CSV upload — true one-click.
2. **Automated daily spend reallocation** — a scheduler that proposes budget shifts each morning and, with approval, pushes them via the APIs.
3. **Creative-generation pipeline** — generate full image + copy variants, not just text rewrites, wired into dynamic creative.
4. **Multi-account portfolio view** with anomaly detection (spend spikes, CTR collapse) paging the team before losses compound.

---

## Quick start

```bash
# 1. Backend (FastAPI + Ollama)
cd backend
pip install -r requirements.txt
# Ensure Ollama is running locally with a model:
#   ollama pull qwen2.5-coder:14b
uvicorn main:app --reload --port 8000

# 2. Frontend (Next.js)
cd ../frontend
npm install
npm run dev   # http://localhost:3000
```

Requires [Ollama](https://ollama.com) running locally. No external API keys needed.

## Tech

- **Backend:** FastAPI, Python, pandas (CSV parsing), Ollama (local LLM).
- **Frontend:** Next.js (React).
- **LLM:** Local only (qwen2.5-coder / qwen3 / deepseek-r1 via Ollama).
