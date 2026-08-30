"""post-process.py — Timer injection for the Interview Power deck.

Adds a 60s auto-start timer pill to the speed-dating GO slide. Re-run after
every render (render.py wipes timer injections). Idempotent: every injection
is guarded so re-runs never duplicate attributes, links, or plugin entries.

Do NOT version the timer-plugin.css link (?v=N) — reference it plainly and
overwrite the file in place. The deck page carries Cache-Control: no-store.
"""

from pathlib import Path

SLIDE_DIR = Path(__file__).parent / "slides"
path = SLIDE_DIR / "index.html"
h = path.read_text(encoding="utf-8")

# 1. Timer attributes (resolver data-id: slide-{id}-1)
if 'data-id="slide-speeddating-go-1"' in h and 'data-timer="60"' not in h:
    h = h.replace(
        'data-id="slide-speeddating-go-1"',
        'data-id="slide-speeddating-go-1" data-timer="60" data-timer-autostart="true"',
    )
if 'data-id="slide-cutup-instru-1"' in h and 'data-timer="180"' not in h:
    h = h.replace(
        'data-id="slide-cutup-instru-1"',
        'data-id="slide-cutup-instru-1" data-timer="180" data-timer-autostart="true"',
    )

# 2. CSS link (plain, unversioned)
if 'href="timer-plugin.css"' not in h:
    h = h.replace("</head>", '  <link rel="stylesheet" href="timer-plugin.css">\n</head>')

# 3. JS script
if 'src="timer-plugin.js"' not in h:
    h = h.replace(
        '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
        '<script src="timer-plugin.js"></script>\n  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
    )

# 4. Plugin registration
if "TimerPlugin" not in h:
    h = h.replace(
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]",
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]",
    )

path.write_text(h, encoding="utf-8")
print("Post-processing complete")
