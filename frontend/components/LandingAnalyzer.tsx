"use client";

import { useState } from "react";
import DiagnosticCTA from "./DiagnosticCTA";

const API = process.env.NEXT_PUBLIC_API_URL || "";

interface Recs {
  score?: number;
  headline_feedback?: { current: string; issue: string; rewrite: string };
  cta_feedback?: { current: string[]; issue: string; rewrites: string[] };
  top_3_fixes?: { fix: string; expected_impact: string; reasoning: string }[];
  summary?: string;
}

export default function LandingAnalyzer() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<{ page: { url: string; title: string }; recommendations: Recs } | null>(null);
  const [error, setError] = useState("");

  async function analyze(e: React.FormEvent) {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true); setError(""); setData(null);
    try {
      const r = await fetch(`${API}/api/landing`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!r.ok) {
        const e = await r.json().catch(() => ({}));
        throw new Error(e.detail || `Server error ${r.status}`);
      }
      setData(await r.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={analyze} className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-6">
        <label className="mb-2 block text-sm text-zinc-400">Paste a landing-page URL</label>
        <div className="flex gap-3">
          <input
            type="text" value={url} onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/landing-page"
            className="flex-1 rounded-lg border border-zinc-700 bg-zinc-950 px-4 py-2.5 text-zinc-100 outline-none focus:border-emerald-500"
          />
          <button
            type="submit" disabled={loading}
            className="rounded-lg bg-emerald-500 px-5 py-2.5 font-medium text-black transition hover:bg-emerald-400 disabled:opacity-50"
          >
            {loading ? "Analyzing…" : "Analyze"}
          </button>
        </div>
        <p className="mt-2 text-xs text-zinc-600">We fetch the page, extract the copy, and the AI scores it + suggests rewrites.</p>
        {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      </form>

      {data && (
        <>
          {data.recommendations.summary && (
            <div className="rounded-xl border border-emerald-800 bg-emerald-950/20 p-5">
              <div className="flex items-center gap-3">
                <h3 className="font-semibold text-emerald-400">CRO Score</h3>
                <span className="rounded-lg bg-emerald-500 px-3 py-1 text-lg font-bold text-black">
                  {data.recommendations.score}/10
                </span>
              </div>
              <p className="mt-2 text-sm text-zinc-300">{data.recommendations.summary}</p>
              <p className="mt-1 text-xs text-zinc-500">Analyzed: {data.page.title || data.page.url}</p>
            </div>
          )}

          {/* Headline feedback */}
          {data.recommendations.headline_feedback && (
            <Card title="Headline Feedback">
              <KV label="Current" value={data.recommendations.headline_feedback.current} />
              <KV label="Issue" value={data.recommendations.headline_feedback.issue} />
              <KV label="Rewrite" value={data.recommendations.headline_feedback.rewrite} highlight />
            </Card>
          )}

          {/* CTA feedback */}
          {data.recommendations.cta_feedback && (
            <Card title="CTA Feedback">
              <KV label="Current CTAs" value={(data.recommendations.cta_feedback.current || []).join(", ") || "—"} />
              <KV label="Issue" value={data.recommendations.cta_feedback.issue} />
              <div className="mt-2">
                <span className="text-xs uppercase text-zinc-500">Suggested rewrites:</span>
                <div className="mt-1 flex flex-wrap gap-2">
                  {(data.recommendations.cta_feedback.rewrites || []).map((c, i) => (
                    <span key={i} className="rounded-lg border border-emerald-800 bg-emerald-950/30 px-3 py-1 text-sm text-emerald-300">
                      {c}
                    </span>
                  ))}
                </div>
              </div>
            </Card>
          )}

          {/* Diagnostic upsell CTA */}
          <DiagnosticCTA />

          {/* Top 3 fixes */}
          {data.recommendations.top_3_fixes && data.recommendations.top_3_fixes.length > 0 && (
            <Card title="Top 3 Fixes (highest impact)">
              <div className="space-y-3">
                {data.recommendations.top_3_fixes.map((f, i) => (
                  <div key={i} className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-3">
                    <div className="flex items-start gap-2">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-xs font-bold text-black">{i + 1}</span>
                      <div>
                        <div className="font-medium">{f.fix}</div>
                        <div className="mt-1 text-sm text-emerald-400">Impact: {f.expected_impact}</div>
                        <div className="mt-1 text-xs text-zinc-500">{f.reasoning}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
      <h3 className="mb-3 font-semibold">{title}</h3>
      {children}
    </div>
  );
}
function KV({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="mb-2">
      <span className="text-xs uppercase text-zinc-500">{label}: </span>
      <span className={highlight ? "text-emerald-300" : "text-zinc-300"}>{value}</span>
    </div>
  );
}
