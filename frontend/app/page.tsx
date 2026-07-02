"use client";

import { useState } from "react";
import CsvAnalyzer from "@/components/CsvAnalyzer";
import LandingAnalyzer from "@/components/LandingAnalyzer";

type Tab = "csv" | "landing";

export default function Home() {
  const [tab, setTab] = useState<Tab>("csv");

  return (
    <main className="min-h-screen bg-[#0a0a0a] text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-gradient-to-b from-zinc-900 to-[#0a0a0a]">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500 font-bold text-black">
              ⚡
            </div>
            <h1 className="text-2xl font-bold tracking-tight">AdPulse</h1>
            <span className="ml-2 rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">
              local-LLM · no data leaves your machine
            </span>
          </div>
          <p className="mt-3 max-w-2xl text-zinc-400">
            Agentic ad-creative &amp; landing-page analyzer for performance media buyers.
            Upload your ad-account export to find wasted spend and scaling winners — or
            paste a landing-page URL for CRO rewrite recommendations.
          </p>
        </div>
      </header>

      {/* Tabs */}
      <div className="mx-auto max-w-5xl px-6 pt-6">
        <div className="flex gap-2">
          <TabButton active={tab === "csv"} onClick={() => setTab("csv")}>
            📊 Analyze Ad Account (CSV)
          </TabButton>
          <TabButton active={tab === "landing"} onClick={() => setTab("landing")}>
            🌐 Analyze Landing Page (URL)
          </TabButton>
        </div>
      </div>

      {/* Content */}
      <div className="mx-auto max-w-5xl px-6 py-8">
        {tab === "csv" ? <CsvAnalyzer /> : <LandingAnalyzer />}
      </div>

      <footer className="border-t border-zinc-800 py-6 text-center text-xs text-zinc-600">
        AdPulse — Built for the It&apos;s Today Media Build Challenge · Powered by local LLMs (Ollama)
      </footer>
    </main>
  );
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
        active ? "bg-emerald-500 text-black" : "bg-zinc-900 text-zinc-400 hover:bg-zinc-800"
      }`}
    >
      {children}
    </button>
  );
}
