# AdPulse — Direct-Response Ad Copy & Creative Best-Practices Corpus
# Curated from industry-proven frameworks (Ogilvy, Hopkins, contemporary performance-marketing research).
# Each entry is a retrievable "evidence card" the RAG layer cites when generating recommendations.

## Card 1 — Specificity Beats Vagueness
Numeric specifics in ad copy ("48 hours", "$37", "3,200 customers") consistently outperform vague claims ("great value", "many users") in direct-response CVR. The XGBoost feature-importance in this very tool ranked `has_number` as the #1 conversion driver (23.6% importance).
**Action:** Replace abstract claims with concrete numbers. "Save money" → "Save $240/year".
**Source:** Ogilvy on Advertising; Hopkins Scientific Advertising; AdPulse internal model.

## Card 2 — Urgency Drives Action (But Only If Genuine)
Time-limited language ("today", "ends Friday", "limited") lifts CTR 15-30% when the scarcity is real. Fabricated urgency (countdown timers on always-available offers) causes ad-fatigue and long-term trust loss. Use urgency only when a genuine deadline exists.
**Action:** Pair urgency words with a real cutoff; avoid evergreen countdown timers.
**Source:** Psychological trigger research; Cialdini, Influence.

## Card 3 — Social Proof Reduces Risk
Testimonials, review counts ("4.8★ from 2,100 buyers"), and user counts ("trusted by 12,000 founders") lower perceived risk and lift CVR on cold traffic by 10-20%. Most effective for high-consideration or high-price offers where trust is the conversion barrier.
**Action:** Add a specific, verifiable social-proof element to every cold-audience creative.
**Source:** Nielsen trust-in-advertising study; performance-marketing benchmarks.

## Card 4 — Single Clear CTA
Creatives with one explicit call-to-action ("Start free trial", "Book a demo", "Get the checklist") convert better than multi-CTA or passive ("learn more") copy. Decision fatigue reduces CVR when users are given multiple paths.
**Action:** Ensure exactly one verb-first CTA per creative. "Learn more" → "Start your free trial".
**Source:** HubSpot CTA A/B test data; Unbounce landing-page benchmarks.

## Card 5 — Pain > Benefit > Feature
Leading with the customer's pain ("Tired of wasting ad spend on ads that don't convert?") outperforms feature-first copy ("We have an AI analyzer") by 20-40% in cold-audience CVR. The PAS framework (Problem-Agitate-Solve) is the most reliable cold-traffic structure.
**Action:** Audit each creative: does the first line name a specific pain the audience feels?
**Source:** Copyhackers; Joanna Wiebe, Copy School.

## Card 6 — Founder/Brand Story Underperforms on Cold Traffic
"Our story" / "We started in a garage" copy converts poorly on cold prospecting audiences (often <0.5% CVR) because it's seller-centric, not buyer-centric. It can work in retargeting/remarketing where brand familiarity exists, but should be deprioritized in cold acquisition budgets.
**Action:** Cap founder-story creatives at 5-10% of cold-acquisition spend; move them to retargeting.
**Source:** AdPulse clustering analysis (founder-story cluster: 0.14% CVR vs 2.51% for urgency/discount).

## Card 7 — Excessive Capitalization and Emojis Reduce Trust
ALL CAPS headlines and heavy emoji use correlate with lower CVR on sophisticated/B2B audiences (they signal spam). They can lift CTR on impulse-buy consumer offers but hurt post-click conversion. Match register to audience sophistication.
**Action:** For B2B or high-consideration offers, use sentence case and minimal emoji.
**Source:** AdPulse feature-importance (pct_uppercase is a negative CVR driver); Stanford Web Credibility.

## Card 8 — The $0-Conversion Kill Rule
If a creative has spent >1x the target CPA with zero conversions, the posterior probability it will ever convert is very low. Kill it rather than "let it learn". Reallocate the budget to proven winners at 1.5-2x their current spend and monitor for saturation.
**Action:** Auto-pause any creative with spend > target_CPA and conv = 0.
**Source:** Direct-response media-buying standard practice; AdPulse waste-detection heuristic.

## Card 9 — Headline = 80% of the Ad
On average, 5x more people read the headline than the body copy. The headline must (a) name the audience, (b) name the pain or the specific outcome, and (c) create curiosity. "New Arrival" is not a headline; "Turn ad waste into profit in 48 hours" is.
**Action:** Rewrite every generic headline ("New", "Check this out") into outcome-specific headlines.
**Source:** Ogilvy; David Garfinkel, Advertising Headlines That Make You Rich.

## Card 10 — Frequency Cap to Avoid Fatigue
A creative shown >4x/week to the same user sees steep CVR decay. Refresh creative every 7-14 days on active campaigns. Dynamic creative optimization (DCO) with 3-5 headline/body variants extends lifespan.
**Action:** Monitor frequency; refresh or rotate when frequency > 4.
**Source:** Meta ad-fatigue benchmarks; Nielsen DAR data.
