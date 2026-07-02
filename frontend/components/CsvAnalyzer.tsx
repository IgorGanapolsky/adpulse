"use client";

import { useState, useRef } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AnalysisRow {
  name: string; copy: string; spend: number; impressions: number;
  clicks: number; conversions: number; cpc: number; ctr: number; cpa: number | null; bucket: string;
}
interface Totals {
  creative_count: number; total_spend: number; waste_spend: number;
  winner_spend: number; total_conversions: number; waste_pct: number;
}
interface Strategy {
  waste_to_kill?: { name: string; reason: string; spend_at_stake: number }[];
  winners_to_scale?: { name: string; reason: string; suggested_action: string }[];
  summary?: string;
  error?: string;
}

const BUCKET_STYLES: Record<string, string> = {
  winner: "border-emerald-600 bg-emerald-950/30",
  "break-even": "border-amber-600/50 bg-amber-950/20",
  waste: "border-red-600 bg-red-950/30",
};
const BUCKET_LABEL: Record<string, string> = {
  winner: "🟢 WINNER — scale", "break-even": "🟡 BREAK-EVEN — test", waste: "🔴 WASTE — kill",
};

export default function CsvAnalyzer() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ analysis: { rows: AnalysisRow[]; totals: Totals }; strategy: Strategy } | null>(null);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  async function onUpload(file: File) {
    setLoading(true); setError(""); setResult(null);
    const fd = new FormData();
    fd.append("file", file);
    try {
      const r = await fetch(`${API}/analyze/csv`, { method: "POST", body: fd });
      if (!r.ok) {
        const e = await r.json().catch(() => ({}));
        throw new Error(e.detail || `Server error ${r.status}`);
      }
      setResult(await r.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  async function loadSample() {
    setLoading(true); setError("");
    try {
      const r = await fetch("/sample_ad_account.csv");
      const blob = await r.blob();
      await onUpload(new File([blob], "sample_ad_account.csv"));
    } catch {
      setError("Could not load sample. Ensure the backend is running.");
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload zone */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-8 text-center">
        <input
          ref={fileRef} type="file" accept=".csv" className="hidden"
          onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])}
        />
        <p className="mb-4 text-zinc-400">Upload an ad-account CSV export (Meta, Google Ads, TikTok, Taboola).</p>
        <div className="flex justify-center gap-3">
          <button
            onClick={() => fileRef.current?.click()}
            disabled={loading}
            className="rounded-lg bg-emerald-500 px-5 py-2.5 font-medium text-black transition hover:bg-emerald-400 disabled:opacity-50"
          >
            {loading ? "Analyzing…" : "Upload CSV"}
          </button>
          <button
            onClick={loadSample} disabled={loading}
            className="rounded-lg border border-zinc-700 px-5 py-2.5 text-zinc-300 transition hover:bg-zinc-800 disabled:opacity-50"
          >
            Try sample data
          </button>
        </div>
        <p className="mt-3 text-xs text-zinc-600">Expected columns: spend/cost, impressions, clicks, conversions, ad name, ad copy.</p>
        {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      </div>

      {/* Results */}
      {result && (
        <>
          {/* Totals */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <Stat label="Total spend" value={`$${result.analysis.totals.total_spend.toLocaleString()}`} />
            <Stat label="Wasted spend" value={`$${result.analysis.totals.waste_spend.toLocaleString()}`} highlight="red" />
            <Stat label="Waste %" value={`${result.analysis.totals.waste_pct}%`} highlight="red" />
            <Stat label="Conversions" value={result.analysis.totals.total_conversions.toString()} highlight="green" />
          </div>

          {/* Strategy summary */}
          {result.strategy.summary && (
            <div className="rounded-xl border border-emerald-800 bg-emerald-950/20 p-5">
              <h3 className="mb-2 font-semibold text-emerald-400">📋 AI Action Plan</h3>
              <p className="text-sm text-zinc-300">{result.strategy.summary}</p>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                {result.strategy.waste_to_kill && result.strategy.waste_to_kill.length > 0 && (
                  <div>
                    <h4 className="mb-2 text-sm font-medium text-red-400">Kill (wasted spend)</h4>
                    {result.strategy.waste_to_kill.map((w, i) => (
                      <div key={i} className="mb-2 rounded-lg border border-red-900/50 bg-red-950/20 p-3 text-sm">
                        <div className="font-medium">{w.name} <span className="text-red-400">(${w.spend_at_stake})</span></div>
                        <div className="text-zinc-400">{w.reason}</div>
                      </div>
                    ))}
                  </div>
                )}
                {result.strategy.winners_to_scale && result.strategy.winners_to_scale.length > 0 && (
                  <div>
                    <h4 className="mb-2 text-sm font-medium text-emerald-400">Scale (winners)</h4>
                    {result.strategy.winners_to_scale.map((w, i) => (
                      <div key={i} className="mb-2 rounded-lg border border-emerald-900/50 bg-emerald-950/20 p-3 text-sm">
                        <div className="font-medium">{w.name}</div>
                        <div className="text-zinc-400">{w.reason}</div>
                        <div className="mt-1 text-emerald-400">→ {w.suggested_action}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Creative breakdown */}
          <div>
            <h3 className="mb-3 font-semibold">Creative Breakdown ({result.analysis.rows.length})</h3>
            <div className="space-y-2">
              {result.analysis.rows.map((r, i) => (
                <div key={i} className={`rounded-lg border p-4 ${BUCKET_STYLES[r.bucket]}`}>
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <div className="font-medium">{r.name}</div>
                      {r.copy && <div className="mt-1 truncate text-sm text-zinc-500">{r.copy}</div>}
                    </div>
                    <span className="shrink-0 text-xs font-medium">
                      {BUCKET_LABEL[r.bucket]}
                    </span>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-4 text-xs text-zinc-400">
                    <span>Spend: <b className="text-zinc-200">${r.spend.toLocaleString()}</b></span>
                    <span>Conv: <b className="text-zinc-200">{r.conversions}</b></span>
                    <span>CPC: <b className="text-zinc-200">${r.cpc}</b></span>
                    <span>CTR: <b className="text-zinc-200">{r.ctr}%</b></span>
                    {r.cpa !== null && <span>CPA: <b className="text-zinc-200">${r.cpa}</b></span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Stat({ label, value, highlight }: { label: string; value: string; highlight?: "red" | "green" }) {
  const color = highlight === "red" ? "text-red-400" : highlight === "green" ? "text-emerald-400" : "text-zinc-100";
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4">
      <div className="text-xs uppercase tracking-wide text-zinc-500">{label}</div>
      <div className={`mt-1 text-2xl font-bold ${color}`}>{value}</div>
    </div>
  );
}
