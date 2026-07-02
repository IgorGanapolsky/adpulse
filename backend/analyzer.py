"""Creative analyzer — classifies ad creatives into winners/break-even/waste
and generates improved copy variants via the local LLM."""
from __future__ import annotations
import pandas as pd
from llm import chat, chat_json


# --- column resolution -------------------------------------------------------
# Ad-platform exports all use different column names. We normalize heuristically.
def _resolve_columns(df: pd.DataFrame) -> dict:
    cols = {c.lower().strip(): c for c in df.columns}
    find = lambda *names: next((cols[n] for n in names if n in cols), None)

    spend = find("spend", "cost", "amount spent", "spend (usd)", "cost_per_result")
    impr = find("impressions", "imps", "impr")
    clicks = find("clicks", "link clicks", "clicks (link)")
    conv = find(
        "conversions", "purchases", "results", "leads",
        "conversions (purchase)", "checkout_roas",
    )
    # creative identifier / text
    name = find("ad name", "campaign name", "name", "ad", "creative", "ad_name", "adset name")
    text = find("ad copy", "body", "text", "primary text", "creative text", "headline", "title")

    return {"spend": spend, "impr": impr, "clicks": clicks, "conv": conv,
            "name": name, "text": text}


def _safe_num(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def analyze_creatives(df: pd.DataFrame) -> dict:
    """Classify each row into winner / break-even / waste and compute key metrics.

    Returns a dict with buckets, totals, and a ranked list.
    """
    c = _resolve_columns(df)
    if not c["spend"]:
        raise ValueError(
            "Could not find a spend/cost column. Expected one of: spend, cost, amount spent."
        )

    spend = _safe_num(df[c["spend"]])
    clicks = _safe_num(df[c["clicks"]]) if c["clicks"] else pd.Series([0] * len(df))
    conv = _safe_num(df[c["conv"]]) if c["conv"] else pd.Series([0] * len(df))
    impr = _safe_num(df[c["impr"]]) if c["impr"] else pd.Series([0] * len(df))

    cpc = (spend / clicks).replace([float("inf"), float("nan")], 0)
    cpa = spend / conv.replace(0, pd.NA)
    ctr = (clicks / impr.replace(0, pd.NA)).fillna(0)

    # Heuristic bucketing (platform-agnostic, relative to portfolio):
    #   waste  = spending money with zero conversions
    #   winner = above-median conversion count AND not worst-quartile CPA
    #   break-even = everything else
    has_spend = spend > 0
    has_conv = conv > 0
    median_conv = conv[has_spend].median() if has_spend.any() else 0

    rows = []
    for i in df.index:
        s, n_conv, cl, im = float(spend[i]), float(conv[i]), float(clicks[i]), float(impr[i])
        if s > 0 and n_conv == 0:
            bucket = "waste"
        elif n_conv >= median_conv and n_conv > 0:
            bucket = "winner"
        else:
            bucket = "break-even"
        rows.append({
            "name": str(df.at[i, c["name"]]) if c["name"] else f"Row {i}",
            "copy": str(df.at[i, c["text"]])[:500] if c["text"] else "",
            "spend": round(s, 2),
            "impressions": int(im),
            "clicks": int(cl),
            "conversions": int(n_conv),
            "cpc": round(float(cpc[i]), 2) if cl else 0,
            "ctr": round(float(ctr[i]) * 100, 2) if im else 0,
            "cpa": round(float(cpa[i]), 2) if n_conv else None,
            "bucket": bucket,
        })

    total_spend = float(spend.sum())
    waste_spend = float(sum(r["spend"] for r in rows if r["bucket"] == "waste"))
    winner_spend = float(sum(r["spend"] for r in rows if r["bucket"] == "winner"))

    # rank: winners first (by conversions), then break-even (by spend), then waste (by spend)
    order = {"winner": 0, "break-even": 1, "waste": 2}
    rows.sort(key=lambda r: (order[r["bucket"]], -r["conversions"], -r["spend"]))

    return {
        "rows": rows,
        "totals": {
            "creative_count": len(rows),
            "total_spend": round(total_spend, 2),
            "waste_spend": round(waste_spend, 2),
            "winner_spend": round(winner_spend, 2),
            "total_conversions": int(conv.sum()),
            "waste_pct": round(waste_spend / total_spend * 100, 1) if total_spend else 0,
        },
        "columns_used": {k: v for k, v in c.items() if v},
    }


def generate_strategy(analysis: dict) -> dict:
    """Ask the local LLM for a concrete action plan from the analysis."""
    summary = {
        "totals": analysis["totals"],
        "waste_rows": [r for r in analysis["rows"] if r["bucket"] == "waste"][:5],
        "winner_rows": [r for r in analysis["rows"] if r["bucket"] == "winner"][:5],
    }
    prompt = (
        "You are a senior performance-marketing media buyer. Given this ad-account "
        "analysis, produce a concrete action plan.\n\n"
        f"Analysis (JSON):\n{summary}\n\n"
        "Return JSON with keys:\n"
        '- "waste_to_kill": list of {name, reason, spend_at_stake}\n'
        '- "winners_to_scale": list of {name, reason, suggested_action}\n'
        '- "summary": 2-3 sentence executive summary focusing on dollars\n'
        "Be specific and tie every recommendation to a dollar figure."
    )
    return chat_json(prompt)


def generate_copy_variants(winner_copy: str, brand: str = "", n: int = 3) -> dict:
    """Generate improved ad-copy variants for a winning creative."""
    prompt = (
        "You are an expert direct-response copywriter for paid social ads.\n"
        f"Here is the top-performing ad copy to model:\n\"\"\"\n{winner_copy}\n\"\"\"\n"
        f"{'Brand context: ' + brand if brand else ''}\n\n"
        f"Generate {n} improved variants. Return JSON:\n"
        '{{"variants": [{{"copy": "...", "reasoning": "why this change should beat the original"}}]}}'
    )
    return chat_json(prompt)
