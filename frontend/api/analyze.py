"""POST /api/analyze — CSV ad account analysis."""
from __future__ import annotations
import io, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from analyzer import analyze_creatives, generate_strategy
from predictor import train as train_predictor, predict as predict_cvr
from clustering import cluster_creatives
from rag_agent import agentic_recommendations

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.post("/")
@app.post("/analyze")
@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".csv"):
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
    except Exception as e:
        strategy = {"error": f"LLM strategy generation failed: {e}"}

    ml = {}
    try:
        ml["training"] = train_predictor(df)
        ml["predictions"] = predict_cvr(df)
    except Exception as e:
        ml = {"error": f"Predictive model failed: {e}"}

    clusters = {}
    try:
        clusters = cluster_creatives(df)
    except Exception as e:
        clusters = {"error": f"Clustering failed: {e}"}

    rag = {}
    try:
        cluster_summary = clusters.get("clusters") if isinstance(clusters, dict) else None
        rag = agentic_recommendations(df, cluster_summary)
    except Exception as e:
        rag = {"error": f"Agentic RAG failed: {e}"}

    return {"analysis": analysis, "strategy": strategy, "ml": ml, "clusters": clusters, "rag": rag}
