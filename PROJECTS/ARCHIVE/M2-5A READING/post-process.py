# Post-processing script
# Re-run after every render — render.py wipes timer injections.

SLIDE_DIR = "PROJECTS/M2-5A READING/slides"
path = f"{SLIDE_DIR}/index.html"
h = open(path, encoding="utf-8").read()

# ── Timer injections ──
# Read task: 10 minutes (600s) — auto-start
h = h.replace('data-id="slide-read-task-1"',
              'data-id="slide-read-task-1" data-timer="600" data-timer-autostart="true"')
# Discussion: 7 minutes (420s)
h = h.replace('data-id="slide-discussion-1"',
              'data-id="slide-discussion-1" data-timer="420"')

# ── Plugin registration ──
h = h.replace('</head>', '  <link rel="stylesheet" href="timer-plugin.css?v=2">\n</head>')
h = h.replace(
    '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
    '<script src="timer-plugin.js"></script>\n  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>'
)
h = h.replace(
    'plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]',
    'plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]'
)

open(path, "w", encoding="utf-8").write(h)
print("Post-processing complete")
