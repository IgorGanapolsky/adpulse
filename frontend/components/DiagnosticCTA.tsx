"use client";

const PAYMENT_LINK =
  process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK ||
  "https://buy.stripe.com/cNi4gzcqMaPs3hD35V3sI36";

export default function DiagnosticCTA() {
  return (
    <div className="rounded-2xl border-2 border-emerald-500 bg-gradient-to-br from-emerald-950/40 via-zinc-900/60 to-zinc-900/60 p-8 shadow-lg shadow-emerald-900/20">
      <div className="flex flex-col items-start gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex-1">
          <div className="mb-2 flex items-center gap-2">
            <span className="rounded-full bg-emerald-500 px-3 py-1 text-xs font-bold uppercase tracking-wide text-black">
              Full Report
            </span>
            <span className="text-xs text-zinc-500">Delivered within 24h</span>
          </div>
          <h3 className="text-xl font-bold text-zinc-100">
            Get Full Diagnostic Report — $499
          </h3>
          <p className="mt-2 max-w-xl text-sm text-zinc-400">
            The preview above covers the basics. The full report includes a
            deep-dive on every creative, audience-split recommendations,
            budget reallocation roadmap, and a live strategy call with a
            senior media buyer.
          </p>
          <ul className="mt-3 space-y-1 text-sm text-zinc-300">
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">✓</span> Creative-by-creative
              breakdown with projected CVR uplift
            </li>
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">✓</span> Kill / scale /
              test budget reallocation plan
            </li>
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">✓</span> 30-min strategy
              call with a senior media buyer
            </li>
          </ul>
        </div>
        <a
          href={PAYMENT_LINK}
          target="_blank"
          rel="noopener noreferrer"
          className="w-full shrink-0 rounded-xl bg-emerald-500 px-8 py-4 text-center text-lg font-bold text-black shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-400 hover:shadow-emerald-400/40 sm:w-auto"
        >
          Get Full Report — $499
        </a>
      </div>
      <p className="mt-4 text-xs text-zinc-600">
        🔒 Secure checkout powered by Stripe. Instant access after payment.
      </p>
    </div>
  );
}
