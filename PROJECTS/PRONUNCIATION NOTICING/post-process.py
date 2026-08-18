"""Post-process the Pronunciation Noticing deck.

Idempotent: safe to re-run after every render (render.py wipes injections).
Adds the 5-minute timer to the Catch the Finals slide and registers the
timer plugin without duplication.
"""

from pathlib import Path

path = Path("PROJECTS/PRONUNCIATION NOTICING/slides/index.html")
h = path.read_text(encoding="utf-8")
changed = False

# ── Timer on game-f (5 minutes) ──
timer_attr = 'data-timer="300"'
target = 'data-id="slide-game-f-1"'
if timer_attr not in h:
    h = h.replace(target, f'{target} {timer_attr}')
    changed = True

# ── Plugin CSS link (no version, in place) ──
if 'href="timer-plugin.css"' not in h:
    h = h.replace('</head>', '  <link rel="stylesheet" href="timer-plugin.css">\n</head>')
    changed = True

# ── Plugin JS script ──
if 'src="timer-plugin.js"' not in h:
    h = h.replace(
        '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
        '<script src="timer-plugin.js"></script>\n  '
        '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>'
    )
    changed = True

# ── Plugin registration ──
if "TimerPlugin" not in h:
    h = h.replace(
        'plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]',
        'plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]'
    )
    changed = True

path.write_text(h, encoding="utf-8")
print("Post-processing complete" + ("" if changed else " (no changes needed)"))
