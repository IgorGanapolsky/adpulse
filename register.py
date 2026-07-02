"""Register Igor for the It's Today Media Build Challenge via Playwright.

Form fields (from /register):
  - Full name *
  - Email *
  - GitHub profile URL *
  - 'What AI marketing problem would you tackle, and why?' (50-250 words) *
  - US resident: Yes/No *
  - How did you hear about this contest? (optional)
  - 8 acknowledgment checkboxes (rules)
"""
import sys
from playwright.sync_api import sync_playwright

NAME = "Igor Ganapolsky"
EMAIL = "iganapolsky@gmail.com"
GITHUB = "https://github.com/IgorGanapolsky"
# 50-250 words answering: what AI marketing problem would you tackle, and why?
ANSWER = (
    "I would build an agentic creative and landing-page analyzer for media buying teams. "
    "Performance and affiliate marketers burn hours every week manually reviewing ad-account "
    "exports across Meta, Google, TikTok, and Taboola, trying to decide which creatives to kill, "
    "which to scale, and how to rewrite underperforming copy. The data already exists; the "
    "decision is slow and largely manual. An LLM is uniquely suited to cluster noisy creative "
    "performance data, surface wasted spend, and generate on-brand copy variants with a clear "
    "reasoning trail for each recommendation. This sits directly on the revenue line: kill waste "
    "faster, scale winners faster, and turn spend data into a concrete action plan the same day. "
    "The reason it matters is simple — every dollar of wasted ad spend is margin the team never "
    "gets back, and every day a winning creative under-scaled is conversions left on the table. "
    "I have already shipped a working version of this tool, AdPulse, that runs on a local LLM so "
    "no ad-account data ever leaves the marketer's machine, which is a hard adoption requirement "
    "for teams handling real spend and conversion data. Next I would wire live ad-platform APIs "
    "to replace CSV upload and add automated daily budget reallocation. This is exactly the kind "
    "of AI-first tooling that takes a lean marketing team to the next level."
)

# count words to stay within 50-250
wc = len(ANSWER.split())
assert 50 <= wc <= 250, f"Answer is {wc} words (need 50-250)"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Loading /register ...")
        page.goto("https://www.itstoday.media/register", wait_until="networkidle", timeout=40000)

        # Fill text inputs by placeholder (most robust for this form)
        page.fill('input[placeholder="Your name"]', NAME)
        page.fill('input[placeholder="you@example.com"]', EMAIL)
        page.fill('input[placeholder="https://github.com/you"]', GITHUB)
        page.fill('textarea', ANSWER)

        # US resident = Yes (first radio). Click the "Yes" radio explicitly.
        radios = page.locator('input[name="is_us_resident"]')
        radios.nth(0).check()

        # Check all 8 acknowledgment checkboxes
        checkboxes = page.locator('input[type="checkbox"]')
        n = checkboxes.count()
        print(f"Found {n} acknowledgment checkboxes — checking all.")
        for i in range(n):
            if not checkboxes.nth(i).is_checked():
                checkboxes.nth(i).check()

        # Capture state before submit for verification
        print(f"Name={NAME} Email={EMAIL} GitHub={GITHUB} Words={wc} US=Yes Checkboxes={n}")

        # Take a screenshot as proof of the filled form
        page.screenshot(path="/tmp/adpulse_register_filled.png", full_page=True)
        print("Screenshot saved: /tmp/adpulse_register_filled.png")

        # Find and click the Register submit button
        submit = page.get_by_role("button", name="Register").last
        submit.click()
        page.wait_for_timeout(5000)

        # Capture post-submit state
        page.screenshot(path="/tmp/adpulse_register_after.png", full_page=True)
        url_after = page.url
        body = page.inner_text("body")[:1500]
        print(f"URL after submit: {url_after}")
        print(f"Body preview:\n{body}")
        browser.close()

if __name__ == "__main__":
    main()
