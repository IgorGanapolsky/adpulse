"""Vercel Python serverless function for AdPulse API.

Uses Vercel's native Python function format with FastAPI ASGI app.
All API routes are handled by this single FastAPI app via Vercel's
`entrypoint` configuration in pyproject.toml.
"""
from __future__ import annotations
import io
import sys
import os

# Ensure lib imports work
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analyzer import analyze_creatives, generate_strategy, generate_copy_variants
from landing import analyze_landing_page
from predictor import train as train_predictor, predict as predict_cvr
from clustering import cluster_creatives
from rag_agent import agentic_recommendations

app = FastAPI(title="AdPulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.get("/")
@app.get("/api")
@app.get("/api/")
def health():
    return {"status": "ok", "service": "AdPulse", "layers": ["heuristic", "xgboost", "clustering", "rag"]}


class CopyRequest(BaseModel):
    winner_copy: str
    brand: str = ""


class LandingRequest(BaseModel):
    url: str


@app.post("/analyze")
@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file.")
    raw = (await file.read()).decode("utf-8", errors="replace")
    try:
        df = pd.read_csv(io.StringIO(raw))
    except Exception as e:
        raise HTTPException(400, f"Could not parse CSV: {e}")
    if len(df) == 0:
        raise HTTPException(400, "CSV is empty.")

    # Layer 1: heuristic bucketing + LLM action plan
    analysis = analyze_creatives(df)
    try:
        strategy = generate_strategy(analysis)
    except Exception as e:
        strategy = {"error": f"LLM strategy generation failed: {e}"}

    # Layer 2: XGBoost predictive model
    ml = {}
    try:
        ml["training"] = train_predictor(df)
        ml["predictions"] = predict_cvr(df)
    except Exception as e:
        ml = {"error": f"Predictive model failed: {e}"}

    # Layer 3: creative clustering
    clusters = {}
    try:
        clusters = cluster_creatives(df)
    except Exception as e:
        clusters = {"error": f"Clustering failed: {e}"}

    # Layer 4: agentic RAG
    rag = {}
    try:
        cluster_summary = clusters.get("clusters") if isinstance(clusters, dict) else None
        rag = agentic_recommendations(df, cluster_summary)
    except Exception as e:
        rag = {"error": f"Agentic RAG failed: {e}"}

    return {"analysis": analysis, "strategy": strategy, "ml": ml, "clusters": clusters, "rag": rag}


@app.post("/copy")
@app.post("/api/copy")
def copy(req: CopyRequest):
    try:
        return generate_copy_variants(req.winner_copy, req.brand)
    except Exception as e:
        raise HTTPException(502, f"LLM call failed: {e}")


@app.post("/landing")
@app.post("/api/landing")
def landing(req: LandingRequest):
    try:
        return analyze_landing_page(req.url)
    except Exception as e:
        raise HTTPException(502, f"Analysis failed: {e}")
