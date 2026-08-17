#!/usr/bin/env python3
"""Post-process the M3 Compound & Complex Sentences deck.

Injects the timer plugin (CSS + JS + registration) and adds a 10-minute
auto-start timer to the timed writing slide. Idempotent: safe to re-run
after every render. The resolver prefixes data-ids as slide-{id}-1.
"""
import sys

SLIDE_DIR = "PROJECTS/AUG 4 M3 COMPOUND-COMPLEX/slides"
path = f"{SLIDE_DIR}/index.html"
h = open(path, encoding="utf-8").read()
orig = h

# Cache-Control: no-store meta tags (browser always re-fetches doc + CSS)
if '<meta http-equiv="Cache-Control"' not in h:
    h = h.replace(
        '<meta name="viewport"',
        '<meta http-equiv="Cache-Control" content="no-store, no-cache">\n  '
        '<meta http-equiv="Pragma" content="no-cache">\n  '
        '<meta name="viewport"',
    )

# 10-minute timed writing slide (auto-start) — guard prevents duplicates on re-run
if 'data-id="slide-task-use-1"' in h and 'data-timer="600"' not in h:
    h = h.replace(
        'data-id="slide-task-use-1"',
        'data-id="slide-task-use-1" data-timer="600" data-timer-autostart="true"',
    )

# Plugin CSS — referenced plainly (no ?v=), overwrite in place
if 'href="timer-plugin.css"' not in h:
    h = h.replace(
        "</head>",
        '  <link rel="stylesheet" href="timer-plugin.css">\n</head>',
    )

# Plugin JS
if 'src="timer-plugin.js"' not in h:
    h = h.replace(
        '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
        '<script src="timer-plugin.js"></script>\n'
        '  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
    )

# Plugin registration
if "TimerPlugin" not in h:
    h = h.replace(
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]",
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]",
    )

if h == orig:
    print("No changes applied — deck already post-processed?")
else:
    open(path, "w", encoding="utf-8").write(h)
    print("Post-processing complete")

if 'data-timer="600"' not in h:
    print("WARNING: timed slide injection failed", file=sys.stderr)
    sys.exit(1)
