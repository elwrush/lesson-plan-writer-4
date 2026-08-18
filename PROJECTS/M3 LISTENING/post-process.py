#!/usr/bin/env python3
"""Post-process the M3 LISTENING deck.

Injects the timer plugin (CSS + JS + registration) and adds auto-start
timers to the timed slides. Idempotent: safe to re-run after every render.
The resolver prefixes data-ids as slide-{id}-1.
"""
import sys

SLIDE_DIR = "PROJECTS/M3 LISTENING/slides"
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

# Timed slides (auto-start) — per-slide guard so slides sharing a duration
# each get their timer.
timers = {
    "tf-task": "240",
    "discussion": "300",
}
for slide_id, seconds in timers.items():
    data_id = f'data-id="slide-{slide_id}-1"'
    data_timer = f'data-timer="{seconds}"'
    if data_id in h and f'{data_id} data-timer=' not in h:
        h = h.replace(
            data_id,
            f'{data_id} {data_timer} data-timer-autostart="true"',
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

missing = [sid for sid, sec in timers.items() if f'data-timer="{sec}"' not in h]
if missing:
    print(f"WARNING: timer injection failed for: {missing}", file=sys.stderr)
    sys.exit(1)
