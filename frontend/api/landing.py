"""POST /api/landing — landing page CRO analysis."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from landing import analyze_landing_page

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class LandingRequest(BaseModel):
    url: str

@app.post("/")
@app.post("/landing")
@app.post("/api/landing")
def landing(req: LandingRequest):
    try:
        return analyze_landing_page(req.url)
    except Exception as e:
        raise HTTPException(502, f"Analysis failed: {e}")
