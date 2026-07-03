import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
const OPENROUTER_MODEL = process.env.ADPULSE_MODEL || "meta-llama/llama-3.3-70b-instruct";

async function llmChat(prompt: string, jsonMode = false, temperature = 0.4): Promise<string> {
  if (!OPENROUTER_API_KEY) throw new Error("OPENROUTER_API_KEY not set");
  const payload: Record<string, unknown> = {
    model: OPENROUTER_MODEL,
    messages: [{ role: "user", content: prompt }],
    temperature,
    max_tokens: 1500,
  };
  if (jsonMode) payload.response_format = { type: "json_object" };

  const r = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`OpenRouter ${r.status}`);
  const data = await r.json();
  return data.choices[0].message.content.trim();
}

export async function POST(req: NextRequest) {
  try {
    const { url } = await req.json();
    if (!url) return NextResponse.json({ detail: "URL required" }, { status: 400 });

    // Fetch the landing page HTML
    const pageResp = await fetch(url, {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; AdPulseBot/1.0)" },
      signal: AbortSignal.timeout(15000),
    });
    const html = await pageResp.text();

    // Extract text content (strip tags crudely)
    const text = html
      .replace(/<script[\s\S]*?<\/script>/gi, "")
      .replace(/<style[\s\S]*?<\/style>/gi, "")
      .replace(/<[^>]+>/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .substring(0, 3000);

    // Extract headline
    const h1Match = html.match(/<h1[^>]*>(.*?)<\/h1>/i);
    const headline = h1Match ? h1Match[1].replace(/<[^>]+>/g, "").trim() : text.substring(0, 100);

    // Extract CTAs
    const ctaMatches = html.match(/<(?:a|button)[^>]*>(.*?)<\/(?:a|button)>/gi) || [];
    const ctas = ctaMatches
      .map((m) => m.replace(/<[^>]+>/g, "").trim())
      .filter((t) => t.length > 2 && t.length < 50)
      .slice(0, 5);

    // LLM analysis
    const prompt = `You are a conversion rate optimization expert. Analyze this landing page and return JSON with:
- "score": 0-100 conversion score
- "headline_feedback": {current, issue, rewrite}
- "cta_feedback": {current (array), issue, rewrites (array)}
- "copy_feedback": {issue, suggestion}
- "trust_signals": array of missing trust signals
- "top_fixes": array of {priority, fix, expected_impact}

Headline: "${headline}"
CTAs found: ${JSON.stringify(ctas)}
Page text (first 2000 chars): "${text.substring(0, 2000)}"

Return ONLY valid JSON.`;

    const raw = await llmChat(prompt, true, 0.3);
    const result = JSON.parse(raw);

    return NextResponse.json(result);
  } catch (error: unknown) {
    return NextResponse.json({ detail: `Analysis failed: ${error}` }, { status: 502 });
  }
}
