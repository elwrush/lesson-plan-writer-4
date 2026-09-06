#!/usr/bin/env python3
"""post-process.py — Timer + plugin injection for the LISTENING M3 slides.

Re-run after every render to re-inject timers.
"""

import re
from pathlib import Path

SLIDES_DIR = Path(__file__).resolve().parent / "slides"
INDEX = SLIDES_DIR / "index.html"
CSS_FILE = SLIDES_DIR / "timer-plugin.css"
JS_FILE = SLIDES_DIR / "timer-plugin.js"

TIMER_DATA = {
    "slide-speed-cp-1": 120,          # 2 min speed dating round (Set A)
    "slide-speed-fp-1": 120,          # 2 min speed dating round (Set B)
}


def main():
    html = INDEX.read_text(encoding="utf-8")

    # Inject Cache-Control no-store (prevents browser caching)
    if "Cache-Control" not in html:
        html = html.replace(
            "<head>",
            '<head>\n<meta http-equiv="Cache-Control" content="no-store">',
        )

    # Inject timer-plugin CSS if not present
    if "timer-plugin.css" not in html:
        html = html.replace(
            "</head>",
            '  <link rel="stylesheet" href="timer-plugin.css">\n</head>',
        )

    # Inject timer-plugin JS if not present.
    # CRITICAL: must load BEFORE Reveal.initialize() references TimerPlugin.
    # Reveal.initialize() runs in a script block that comes after the CDN
    # reveal.js script tag, so injecting before that CDN tag guarantees
    # TimerPlugin is defined when the plugins array is evaluated.
    if "timer-plugin.js" not in html:
        html = html.replace(
            '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>',
            '<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>\n'
            '  <script src="timer-plugin.js"></script>',
        )

    # Inject TimerPlugin into the Reveal config (idempotent)
    if "TimerPlugin" not in html:
        html = html.replace(
            "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]",
            "plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]",
        )

    # Inject captions-plugin CSS + JS (idempotent — never duplicate).
    # Version with a content hash so a stale browser cache re-fetches the
    # fresh logic after an update (sub-resources are cached independently of
    # the no-store document).
    captions_js = SLIDES_DIR / "captions-plugin.js"
    captions_css = SLIDES_DIR / "captions-plugin.css"
    js_ver = captions_js.stat().st_mtime_ns if captions_js.exists() else 0
    css_ver = captions_css.stat().st_mtime_ns if captions_css.exists() else 0
    if "captions-plugin.css" not in html:
        html = html.replace(
            "</head>",
            f'  <link rel="stylesheet" href="captions-plugin.css?v={css_ver}">\n</head>',
        )
    if "captions-plugin.js" not in html:
        html = html.replace(
            "</body>",
            f'  <script src="captions-plugin.js?v={js_ver}"></script>\n</body>',
        )

    # Inject pause-on-slidechange for YouTube embeds (idempotent — never duplicate).
    # On any slide change, postMessage a pauseVideo command to every YouTube
    # iframe so audio stops when the student advances. enablejsapi=1 (added in
    # build_deck.py youtube_embed) is required for the command to be received.
    if "youtube-pause" not in html:
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
        html = html.replace("</body>", pause_script)

    # Inject data-timer attributes on slides that need them
    for slide_id, duration in TIMER_DATA.items():
        pattern = rf'data-id="{slide_id}"'
        if pattern in html:
            timer_attr = f'data-timer="{duration}"'
            # Check per-slide: does this specific slide already have data-timer?
            slide_line = [l for l in html.split("\n") if f'data-id="{slide_id}"' in l]
            if slide_line and "data-timer=" not in slide_line[0]:
                html = re.sub(
                    pattern,
                    f'{pattern} {timer_attr}',
                    html,
                )

    # Inject data-timer-autostart on all timer slides
    for slide_id in TIMER_DATA:
        pattern = rf'data-id="{slide_id}"'
        if pattern in html:
            slide_line = [l for l in html.split("\n") if f'data-id="{slide_id}"' in l]
            if slide_line and "data-timer-autostart" not in slide_line[0]:
                html = re.sub(
                    pattern,
                    f'{pattern} data-timer-autostart="true"',
                    html,
                )

    INDEX.write_text(html, encoding="utf-8")
    print(f"Post-processed {INDEX.name}")


if __name__ == "__main__":
    main()
