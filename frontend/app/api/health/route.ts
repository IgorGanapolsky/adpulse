import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

// AdPulse health check
export async function GET() {
  return NextResponse.json({
    status: "ok",
    service: "AdPulse",
    layers: ["heuristic", "predictive", "clustering", "rag"],
  });
}
