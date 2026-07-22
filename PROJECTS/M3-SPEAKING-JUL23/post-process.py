SLIDE_DIR = "PROJECTS/M3-SPEAKING-JUL23/slides"
path = f"{SLIDE_DIR}/index.html"
h = open(path, encoding="utf-8").read()

h = h.replace('data-id="slide-recall-docs-1"',
              'data-id="slide-recall-docs-1" data-timer="90" data-timer-autostart="true"')

h = h.replace('data-id="slide-speeddating-go-1"',
              'data-id="slide-speeddating-go-1" data-timer="90"')

h = h.replace('</head>', (
    '  <link rel="stylesheet" href="timer-plugin.css?v=4">\n'
    '</head>'
))
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
