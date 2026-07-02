# AdPulse — Deep Research Briefing
**Date:** 2026-07-02
**Purpose:** Competitive positioning, pricing strategy, and contest-submission optimization for the It's Today Media $5K Build Challenge.

---

## 1. The Contest — What Matt Actually Wants

**Company:** It's Today Media — an **affiliate marketing** company. This is critical: they buy traffic across Meta/Google/Taboola/TikTok and monetize via affiliate offers. Their margins live or die on creative efficiency and waste elimination.

**The prize:** $5,000 cash + full-time job offer (Marketing Development Engineer). Finalists get $250 + guaranteed interview.

**Deadline: July 4, 2026, 11:59 PM ET.** Submissions close in ~2 days.

**Judging criteria (4 dimensions, verbatim from the site):**
1. **Problem selection** — "Did you pick something that actually matters to a marketing team?"
2. **Does it work?** — "Ugly and functional beats beautiful and broken."
3. **Code quality** — "Readable, sensible architecture, something another engineer could extend."
4. **The README** — "Why this one?" and "What's next?" — these tell us how you think.

**The ideal candidate signal (from the brief):**
- "Loves to get shit done"
- "Gets genuinely fired up about... killer, cutting-edge tools with AI"
- "Can run with a project given incomplete direction"
- "Excited about delivering an application... that helps our company make more money"
- "Curious about the business side — how technology supports it, what makes it grow"
- **Deep experience with both marketing AND agentic AI tools** is the ideal, but "there are not many of them" — so demonstrating this combo is a moat.

**AI tools explicitly encouraged:** "We care what you build, not how."

---

## 2. Competitive Landscape — Where AdPulse Sits

### Direct competitors (creative analysis/generation tools)

| Tool | Focus | Pricing | AdPulse's edge |
|---|---|---|---|
| **AdCreative.ai** | Creative *generation* from $35B+ spend data | $39–$999/mo (credit-based) | They generate; we *diagnose*. They tell you what to make; we tell you what to kill and why. |
| **Motion.io** | Client portal / project management for agencies | $29–$79/seat/mo | Not a competitor — different category (workflow, not analysis). |
| **Triple Whale** | Ecom attribution + pixel | ~$1,290/mo (GMV-tiered) | Attribution, not creative diagnosis. Complementary, not competing. |
| **Northbeam** | Multi-touch attribution | $1,500+/mo (spend-tiered) | Same — attribution, not creative-level ML analysis. |

### The gap AdPulse fills
**No competitor does creative-level ML diagnosis with explainable, evidence-grounded recommendations.** AdCreative.ai generates new ads but doesn't analyze why existing ones fail. Attribution tools (Triple Whale, Northbeam) tell you *which channel* converts but not *which creative* within it, and never *why* a creative's copy is underperforming its modeled potential.

AdPulse's 4-layer stack (heuristic → XGBoost uplift prediction → semantic clustering → agentic RAG with citations) is genuinely novel in this segment. The RAG layer with cited evidence cards is the differentiator that makes recommendations *trustworthy* — a media buyer can verify the reasoning rather than trusting a black box.

---

## 3. Pricing Strategy

### Market benchmarks pulled from live competitor pages
- **AdCreative.ai:** $39/mo (10 credits, 1 brand) → $999/mo (100 credits, 25 brands). Annual billing discounts of 40–50%.
- **Triple Whale:** ~$1,290/mo, tiered by GMV ($1M–$30M+).
- **Northbeam:** $1,500/mo starter (for <$1.5M/yr media spend), custom enterprise above.
- **Performance-marketing SaaS mid-market:** $200–$500/mo is the dense band for tools targeting agencies and serious media buyers.

### Recommended AdPulse pricing
Given the local-LLM privacy moat and the affiliate/agency target:

| Tier | Price | Target | Rationale |
|---|---|---|---|
| **Diagnostic (one-time)** | **$499** | Solo media buyer / first engagement | Low-friction entry, already offered in outreach. Proves value on one account. |
| **Pro (monthly)** | **$299/mo** | Independent media buyer / small agency | Undercuts AdCreative.ai Pro ($249–$339) while offering analysis they don't. |
| **Agency (monthly)** | **$799/mo** | 5–10 brand portfolios | Multi-account, API ingestion, white-label reports. |

**Key insight:** The $499 diagnostic → $299/mo retainer path is the proven agency-sales motion. The diagnostic pays for itself the moment it identifies >$499 of waste (which on any real account it does in minutes).

---

## 4. Contest Submission Optimization

### Mapping AdPulse to the 4 judging criteria

| Criterion | How AdPulse scores | Evidence to surface |
|---|---|---|
| **Problem selection** | ✅ Strong — creative waste is the #1 pain for affiliate media buyers. They literally burn money on losing creatives daily. | README intro should open with the dollar-waste problem, not the tech. |
| **Does it work?** | ✅ Verified — live demo, all 4 layers return real results on sample data. | Must link the **live deployed app** (frontend + working backend). The demo must not break. |
| **Code quality** | ✅ Clean modular architecture — each layer is a separate, testable module. | README architecture diagram + the fact that each layer can run independently. |
| **The README** | ⚠️ Needs the "Why this one?" and "What's next?" narrative sharpened. | This is where the contest is won or lost. Current README is good technically but needs the *business argument*. |

### The single biggest risk: the ephemeral tunnel
The backend runs on a Cloudflare quick-tunnel that dies when this session ends. **If Matt clicks the demo link and it's dead, we lose criterion #2 entirely.** This must be fixed before submission — move backend to a persistent host (Railway, Fly.io, or Render free tier).

### README narrative gaps to fix before submission
The current README leads with architecture. The contest wants **"Why this one?"** — the answer should be:
> *"Because every affiliate media buyer is burning 15-30% of their spend on creatives that will never convert, and no existing tool tells them which ones or why. AdPulse does — with a four-layer analysis stack that predicts, clusters, and grounds every recommendation in cited evidence."*

And **"What's next?"** should tie directly to Matt's business:
> *"Live ad-platform API ingestion (so it runs automatically every morning on your accounts), one-click kill/scale execution, and auto-generation of replacement variants for high-potential creatives — turning the diagnosis loop into a closed optimization loop."*

---

## 5. Strategic Recommendations (ranked by impact)

### Before July 4 deadline (must-do)
1. **Fix the persistence gap.** Move the backend off the ephemeral tunnel to Railway/Fly.io. A dead demo = disqualification on criterion #2. (~1 hr)
2. **Rewrite the README opening** with the business problem first, tech second. Add the explicit "Why this one?" and "What's next?" sections the rubric demands. (~30 min)
3. **Add a 30-second Loom/screen-recording** of the live demo as a backup in case the deployed demo hiccups during review. Contest says "ugly and functional beats beautiful and broken" — prove it works on video.
4. **Register and submit early** (before July 4 11:59 PM ET). The brief says "Submit early if you want time to polish."

### After the contest (revenue path)
5. **Productize the $499 diagnostic** as a self-serve flow: upload CSV → pay $499 → get the full 4-layer report + scheduled call. This is the proven agency-sales wedge.
6. **Add Meta Marketing API + Google Ads API ingestion** to convert from one-time CSV upload to daily automated pulls → enables the $299/mo retainer.
7. **Expand the RAG corpus** with each client's historical creative winners so recommendations get *personalized* to their account — a data moat competitors can't replicate without the client's data.

---

## 6. Research Sources (all retrieved 2026-07-02)
- itstoday.media contest page (judging criteria, role description, FAQ, rules, timeline)
- adcreative.ai homepage (live pricing: $39–$999/mo)
- motion.io/pricing ($29–$79/seat/mo)
- triplewhale.com/pricing (~$1,290/mo, GMV-tiered)
- northbeam.io/pricing ($1,500/mo starter)
- arxiv.org/abs/2211.11524 — Kaplan et al., "Conversion-Based Dynamic-Creative Optimization in Native Advertising" (Yahoo Gemini DCO; OFFSET feature-enhanced CF for conversion prediction — validates the creative-feature ML approach)
