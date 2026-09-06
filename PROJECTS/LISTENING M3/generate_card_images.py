#!/usr/bin/env python3
"""generate_card_images.py — Generate card PNGs for the It's Academic slide deck.

Outputs to slides/assets/:
    card-model.png   — 5-step discussion structure
    cards-cp-1.png   — example structured card (Set A)
    cards-fp.png     — example bare card (Set B)
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

PROJ = Path(__file__).resolve().parent
OUT = PROJ / "slides" / "assets"

# ── Card HTML templates ──────────────────────────────────────────────

CARD_MODEL_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><style>
@page { size: 1280px 720px; margin: 0; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Roboto', 'Segoe UI', Arial, sans-serif; width: 1280px; height: 720px;
       background: #1a1a2e; color: #fff; display: flex; flex-direction: column;
       justify-content: center; padding: 40px 70px; }
h1 { font-size: 46px; margin-bottom: 34px; text-align: center; color: #ffdd00; }
.step { width: 100%; margin: 10px 0; padding: 16px 28px; border-radius: 10px;
        display: flex; align-items: baseline; gap: 18px; }
.step-num { font-size: 30px; font-weight: 700; color: #fff; flex: 0 0 auto; }
.step-body { flex: 1; }
.step-title { font-size: 34px; font-weight: 700; display: inline; }
.step-desc { font-size: 26px; color: #ddd; display: inline; margin-left: 12px; }
.s1 { background: #c0392b; }
.s2 { background: #2980b9; }
.s3 { background: #27ae60; }
.s4 { background: #8e44ad; }
.s5 { background: #e67e22; }
</style></head><body>
<h1>5-Step Discussion Structure</h1>
<div class="step s1"><span class="step-num">1</span><div class="step-body"><span class="step-title">Open</span><span class="step-desc">Start the talk — ask a question or introduce the topic.</span></div></div>
<div class="step s2"><span class="step-num">2</span><div class="step-body"><span class="step-title">Opinion</span><span class="step-desc">Say what you think. Use: "I think…", "In my view…"</span></div></div>
<div class="step s3"><span class="step-num">3</span><div class="step-body"><span class="step-title">Reason</span><span class="step-desc">Give a reason. Use: "because…", "The main reason is…"</span></div></div>
<div class="step s4"><span class="step-num">4</span><div class="step-body"><span class="step-title">Agree / Disagree</span><span class="step-desc">Listen, then agree or disagree politely.</span></div></div>
<div class="step s5"><span class="step-num">5</span><div class="step-body"><span class="step-title">Agreement</span><span class="step-desc">Try to reach a compromise together.</span></div></div>
</body></html>"""

CARD_A_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><style>
@page { size: 828px 1171px; margin: 0; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Roboto', 'Segoe UI', Arial, sans-serif; width: 828px; height: 1171px;
       background: #fff; color: #111; padding: 50px; display: flex; flex-direction: column; }
.badge { display: inline-block; background: #1a1a2e; color: #fff; font-size: 18px;
         font-weight: 700; padding: 8px 16px; border-radius: 4px; margin-bottom: 20px; }
h2 { font-size: 32px; font-weight: 700; line-height: 1.2; margin-bottom: 16px; }
.context { font-size: 20px; line-height: 1.4; color: #333; margin-bottom: 24px; }
.label { font-size: 16px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
         color: #666; border-top: 2px solid #ddd; padding-top: 16px; margin-bottom: 12px; }
.steps { list-style: none; margin-bottom: 20px; }
.steps li { font-size: 20px; line-height: 1.4; margin-bottom: 10px; padding-left: 20px;
            position: relative; }
.steps li::before { content: "▸"; position: absolute; left: 0; color: #9b59b6; font-weight: 700; }
.steps li strong { color: #1a1a2e; }
.lang-box { background: #eef2f7; border-left: 4px solid #1a1a2e; border-radius: 4px;
            padding: 16px 20px; flex: 1; font-size: 18px; }
.lang-func { font-size: 15px; font-weight: 700; color: #9b59b6; text-transform: uppercase;
             letter-spacing: 0.8px; margin-top: 12px; }
.lang-func:first-child { margin-top: 0; }
.lang-box ul { list-style: none; line-height: 1.5; }
.lang-box li { margin-bottom: 4px; padding-left: 16px; position: relative; }
.lang-box li::before { content: "•"; position: absolute; left: 0; color: #1a1a2e; font-weight: 700; }
</style></head><body>
<div><span class="badge">Speaking Cue Card 1</span></div>
<h2>Is it ever OK to break a rule to do the right thing?</h2>
<div class="context">Some rules seem unfair or harmful. A person might break one to help someone in need. Is that ever justified?</div>
<div class="label">Structure your discussion</div>
<ol class="steps">
  <li><strong>Open:</strong> <em>"Let's talk about the rules we follow."</em></li>
  <li><strong>Opinion:</strong> <em>Give your opinion.</em></li>
  <li><strong>Reason:</strong> <em>Give a reason for your opinion.</em></li>
  <li><strong>Agree / disagree:</strong> <em>Listen, then agree or disagree.</em></li>
  <li><strong>Agreement:</strong> <em>Try to reach a compromise together.</em></li>
</ol>
<div class="lang-box">
  <div class="label" style="border-top:none;padding-top:0;margin-top:0;margin-bottom:6px">Language you can use</div>
  <div class="lang-func">To open</div><ul><li>"Let's talk about…"</li><li>"Shall we discuss…?"</li></ul>
  <div class="lang-func">To give an opinion</div><ul><li>"In my view…"</li><li>"I strongly believe…"</li></ul>
  <div class="lang-func">To give a reason</div><ul><li>"because…"</li><li>"The main reason is…"</li></ul>
  <div class="lang-func">To agree / disagree</div><ul><li>"I see your point, however…"</li><li>"I partly agree, but…"</li></ul>
  <div class="lang-func">To reach agreement</div><ul><li>"Maybe we can both…"</li><li>"Let's find a middle way."</li></ul>
</div>
</body></html>"""

CARD_B_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><style>
@page { size: 828px 1171px; margin: 0; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Roboto', 'Segoe UI', Arial, sans-serif; width: 828px; height: 1171px;
       background: #fff; color: #111; padding: 50px; display: flex; flex-direction: column; }
.badge { display: inline-block; background: #c0392b; color: #fff; font-size: 18px;
         font-weight: 700; padding: 8px 16px; border-radius: 4px; margin-bottom: 20px; }
.prompt { font-size: 36px; font-weight: 700; line-height: 1.3; margin-bottom: 30px; }
.hint { font-size: 16px; color: #888; text-transform: uppercase; letter-spacing: 1px; }
</style></head><body>
<div><span class="badge">Speaking Cue Card — Set B</span></div>
<div class="prompt">Would you refuse to buy something made by child workers, even if it is much cheaper?</div>
<div class="hint">What do you think?</div>
</body></html>"""


def render_card(html: str, out_path: Path, width=828, height=1171):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.set_content(html, wait_until="networkidle")
        page.screenshot(path=str(out_path), full_page=False)
        browser.close()


def main():
    cards = [
        ("card-model.png", CARD_MODEL_HTML, 1280, 720),
        ("cards-cp-1.png", CARD_A_HTML, 828, 1171),
        ("cards-fp.png", CARD_B_HTML, 828, 1171),
    ]
    for name, html, w, h in cards:
        out = OUT / name
        render_card(html, out, w, h)
        print(f"  {name}: {out.stat().st_size // 1024}KB ({w}x{h})")


if __name__ == "__main__":
    main()
