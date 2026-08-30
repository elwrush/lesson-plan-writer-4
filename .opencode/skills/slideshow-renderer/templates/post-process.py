# Post-processing script template
#
# The resolver adds "slide-{id}-1" prefixes to data-ids.
# Re-run this after every render — render.py wipes timer injections.

SLIDE_DIR = "PROJECTS/{project_name}/slides"
path = f"{SLIDE_DIR}/index.html"
h = open(path, encoding="utf-8").read()

# ── Timer injections ──
# Match the data-id the resolver generates: prefix + "slide-" + id + "-1"
h = h.replace('data-id="slide-{slide_id}-1"',
              'data-id="slide-{slide_id}-1" data-timer="{seconds}"')

# ── Auto-start timer ──
h = h.replace('data-id="slide-{slide_id}-1"',
              'data-id="slide-{slide_id}-1" data-timer="{seconds}" data-timer-autostart="true"')

# ── Plugin registration ──
h = h.replace('</head>', '  <link rel="stylesheet" href="timer-plugin.css?v=1">\n</head>')
# Bump the version number (v=1, v=2, ...) after every CSS edit to bypass browser cache.
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
