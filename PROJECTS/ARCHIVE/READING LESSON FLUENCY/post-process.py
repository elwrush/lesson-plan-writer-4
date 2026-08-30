# Post-processing for READING LESSON FLUENCY reciprocal teaching deck.
# Idempotent: guards every injection so re-running after a re-render never duplicates.
# Reference the timer-plugin.css WITHOUT a version query string (gotcha).

import re

SLIDE_DIR = "PROJECTS/READING LESSON FLUENCY/slides"
path = f"{SLIDE_DIR}/index.html"
h = open(path, encoding="utf-8").read()

# ── Timer injections (idempotent: skip if data-timer already present) ──
# Resolver generates data-id="slide-{id}-1". Add data-timer + optional autostart.
TIMES = {
    "transfer-read": 180,     # silent reading per chunk
    "transfer-discuss": 360,  # discussion per chunk
    "discuss-final": 600,     # final big discussion
}

for sid, secs in TIMES.items():
    # Block-level timer (no autostart) on the section
    pat = re.compile(
        r'(data-id="slide-' + re.escape(sid) + r'-1")'
        r'(?![^>]*data-timer)'
    )
    h = pat.sub(lambda m: m.group(1) + f' data-timer="{secs}" data-timer-autostart="true"', h)

# ── Plugin registration (idempotent) ──
if 'href="timer-plugin.css"' not in h:
    h = h.replace(
        "</head>",
        '  <link rel="stylesheet" href="timer-plugin.css">\n</head>'
    )

if '<script src="timer-plugin.js"></script>' not in h:
    h = h.replace(
        '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
        '<script src="timer-plugin.js"></script>\n  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>'
    )

if "TimerPlugin" not in h:
    h = h.replace(
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]",
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]"
    )

# ── Cache: no-store meta (idempotent) ──
if 'cache-control' not in h.lower() and 'Cache-Control' not in h:
    meta = ('  <meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate">\n'
            '  <meta http-equiv="Pragma" content="no-cache">\n')
    h = h.replace("<title>", meta + "  <title>", 1)

open(path, "w", encoding="utf-8").write(h)
print("Post-processing complete")
