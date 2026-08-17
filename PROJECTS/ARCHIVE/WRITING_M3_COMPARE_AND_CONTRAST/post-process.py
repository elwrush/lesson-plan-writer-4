#!/usr/bin/env python3
"""Post-process the M3 Compare and Contrast — Lesson 3 deck.

Injects the timer plugin (canonical files already in slides/), data-timer
attributes on the timed writing stages, and Cache-Control: no-store meta tags.
Idempotent: safe to re-run after every render.
"""

SLIDE_DIR = "PROJECTS/WRITING_M3_COMPARE_AND_CONTRAST/slides"
path = f"{SLIDE_DIR}/index.html"
h = open(path, encoding="utf-8").read()
orig = h

# ── Timers (data-id prefix added by the resolver: slide-{id}-1) ──
h = h.replace(
    'data-id="slide-task-body-1"',
    'data-id="slide-task-body-1" data-timer="480" data-timer-autostart="true"',
)
h = h.replace(
    'data-id="slide-task-conclusion-1"',
    'data-id="slide-task-conclusion-1" data-timer="300" data-timer-autostart="true"',
)
h = h.replace(
    'data-id="slide-task-edit-1"',
    'data-id="slide-task-edit-1" data-timer="480" data-timer-autostart="true"',
)

# ── Timer plugin registration (idempotent) ──
if 'href="timer-plugin.css"' not in h:
    h = h.replace(
        "</head>",
        '  <link rel="stylesheet" href="timer-plugin.css">\n</head>',
        1,
    )

if 'src="timer-plugin.js"' not in h:
    h = h.replace(
        '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
        '<script src="timer-plugin.js"></script>\n  '
        '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
        1,
    )

if "TimerPlugin" not in h:
    h = h.replace(
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]",
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]",
        1,
    )

# ── Cache-Control meta tags (idempotent) ──
if '<meta http-equiv="Cache-Control"' not in h:
    h = h.replace(
        '<meta name="viewport"',
        '<meta http-equiv="Cache-Control" content="no-store, no-cache">\n  '
        '<meta http-equiv="Pragma" content="no-cache">\n  '
        '<meta name="viewport"',
        1,
    )

if h == orig:
    print("No changes applied — deck already post-processed?")
else:
    open(path, "w", encoding="utf-8").write(h)
    print("Post-processing complete")
