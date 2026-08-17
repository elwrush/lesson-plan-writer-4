#!/usr/bin/env python3
"""Post-processing for PSYCH READING deck.

Render.py wipes timer injections on every re-run — run this after every render.
All injections are idempotent (guarded) so re-running is safe.
Timer: self-check (B1 answer key, 60 s, autostart).
"""
from pathlib import Path

path = Path("PROJECTS/PSYCH READING/slides/index.html")
h = path.read_text(encoding="utf-8")

# ── Entry ticket: 4-minute timer, auto-start (idempotent) ──
if 'data-timer="240"' not in h:
    h = h.replace(
        'data-id="slide-entry-ticket-1"',
        'data-id="slide-entry-ticket-1" data-timer="240" data-timer-autostart="true"',
    )

# ── Self-check: 60-second timer, auto-start (idempotent) ──
if 'data-timer="60"' not in h:
    h = h.replace(
        'data-id="slide-self-check-1"',
        'data-id="slide-self-check-1" data-timer="60" data-timer-autostart="true"',
    )

# ── Ensure navigation controls are enabled (never disable them) ──
h = h.replace("      controls: false,", "      controls: true,")

# ── Disable browser caching of the deck ──
if "no-store" not in h:
    h = h.replace(
        "<head>",
        '<head>\n  <meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate">\n  <meta http-equiv="Pragma" content="no-cache">',
    )

# ── Plugin registration (idempotent) ──
if 'href="timer-plugin.css"' not in h:
    h = h.replace("</head>", '  <link rel="stylesheet" href="timer-plugin.css">\n</head>')

if '<script src="timer-plugin.js">' not in h:
    h = h.replace(
        '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
        '<script src="timer-plugin.js"></script>\n  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
    )

if ", TimerPlugin" not in h:
    h = h.replace(
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]",
        "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]",
    )

path.write_text(h, encoding="utf-8")
print("Post-processing complete")
