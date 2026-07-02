"""AdPulse API — FastAPI app.

Endpoints:
  GET  /health
  POST /analyze/csv        — upload ad-account CSV → performance buckets + action plan
  POST /analyze/copy       — generate improved ad-copy variants from a winner
  POST /analyze/landing    — paste landing-page URL → CRO rewrite recommendations
"""
from __future__ import annotations
import io
import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analyzer import analyze_creatives, generate_strategy, generate_copy_variants
from landing import analyze_landing_page

app = FastAPI(title="AdPulse", version="1.0.0",
              description="Agentic ad-creative & landing-page analyzer (local LLM).")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "AdPulse"}


class CopyRequest(BaseModel):
    winner_copy: str
    brand: str = ""


class LandingRequest(BaseModel):
    url: str


@app.post("/analyze/csv")
async def analyze_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file.")
    raw = (await file.read()).decode("utf-8", errors="replace")
    try:
        df = pd.read_csv(io.StringIO(raw))
    except Exception as e:
        raise HTTPException(400, f"Could not parse CSV: {e}")
    if len(df) == 0:
        raise HTTPException(400, "CSV is empty.")

    analysis = analyze_creatives(df)
    try:
        strategy = generate_strategy(analysis)
    except Exception as e:  # noqa: BLE001
        strategy = {"error": f"LLM strategy generation failed: {e}"}
    return {"analysis": analysis, "strategy": strategy}


@app.post("/analyze/copy")
def analyze_copy(req: CopyRequest):
    try:
        return generate_copy_variants(req.winner_copy, req.brand)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"LLM call failed: {e}")


@app.post("/analyze/landing")
def analyze_landing(req: LandingRequest):
    try:
        return analyze_landing_page(req.url)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"Analysis failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
