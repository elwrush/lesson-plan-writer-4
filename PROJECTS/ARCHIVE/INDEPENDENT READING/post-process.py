import re

SLIDE_DIR = "PROJECTS/INDEPENDENT READING/slides"
path = f"{SLIDE_DIR}/index.html"
h = open(path, encoding="utf-8").read()

# ── Timer injection ──
# The resolver adds "slide-{id}-1" prefixes to data-ids.
# Slide 1: 36-minute reading timer, blip once at 1 minute remaining, bell at end.
# Slide 2: 10-minute writing timer, blip every minute, bell at end.
if 'data-timer="2160"' not in h:
    h = h.replace('data-id="slide-reading-task-1"',
                  'data-id="slide-reading-task-1" data-timer="2160"')
if 'data-timer="600"' not in h:
    h = h.replace('data-id="slide-writing-task-1"',
                  'data-id="slide-writing-task-1" data-timer="600" data-timer-blip="minute"')

# ── Plugin registration (idempotent — render.py wipes these every re-run) ──
if 'href="timer-plugin.css"' not in h:
    h = h.replace('</head>', '  <link rel="stylesheet" href="timer-plugin.css">\n</head>')
if 'src="timer-plugin.js"' not in h:
    h = h.replace(
        '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
        '<script src="timer-plugin.js"></script>\n  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>'
    )
if "TimerPlugin" not in h:
    h = h.replace(
        'plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]',
        'plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]'
    )

open(path, "w", encoding="utf-8").write(h)
print("Post-processing complete")
