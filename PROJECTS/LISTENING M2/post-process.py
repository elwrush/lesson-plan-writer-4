# Post-processing: inject timer plugin + data-timer on the speed-dating slides.
#
# The resolver prefixes data-ids with "slide-{id}-1". We target the two
# speed-dating slides (120s each). Re-run after every render — render.py wipes
# these injections.

from pathlib import Path

BASE = Path(__file__).resolve().parent
SLIDE_DIR = BASE / "slides"
path = SLIDE_DIR / "index.html"
h = path.read_text(encoding="utf-8")

# 1. Timer durations on the two speed-dating slides (idempotent-ish guards)
for slide_id, seconds in (("speed-cp", "120"), ("speed-fp", "120")):
    token = f'data-id="slide-{slide_id}-1"'
    h = h.replace(token, f'{token} data-timer="{seconds}"')

# 2. Plugin CSS + JS (guarded against duplicates)
if 'href="timer-plugin.css"' not in h:
    h = h.replace("</head>", '  <link rel="stylesheet" href="timer-plugin.css">\n</head>')
if 'src="timer-plugin.js"' not in h:
    h = h.replace(
        '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
        '<script src="timer-plugin.js"></script>\n  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>'
    )
if "TimerPlugin" not in h:
    h = h.replace(
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]",
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]"
    )

# 3. Pause YouTube embeds when leaving a slide (idempotent — never duplicate).
if "youtube-pause" not in h:
    pause_script = (
        '  <script>\n'
        '  // Pause YouTube embeds when leaving a slide.\n'
        '  window.addEventListener("load", function () {\n'
        '    function pauseAllYoutube() {\n'
        '      document.querySelectorAll("iframe[src*=\'youtube-nocookie.com/embed\']").forEach(function (f) {\n'
        '        f.contentWindow.postMessage(JSON.stringify({event: "command", func: "pauseVideo", args: ""}), "*");\n'
        '      });\n'
        '    }\n'
        '    if (window.Reveal) {\n'
        '      Reveal.on("slidechanged", pauseAllYoutube);\n'
        '      document.addEventListener("keydown", function (e) {\n'
        '        if (["ArrowRight", "ArrowLeft", " ", "PageDown", "PageUp", "Home", "End"].indexOf(e.key) !== -1) pauseAllYoutube();\n'
        '      });\n'
        '    }\n'
        '  });\n'
        '  </script>\n'
        '</body>'
    )
    h = h.replace("</body>", pause_script)

path.write_text(h, encoding="utf-8")
print("Post-processing complete (timers + YouTube pause injected)")
