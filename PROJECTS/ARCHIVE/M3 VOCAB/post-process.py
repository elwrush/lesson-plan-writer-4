#!/usr/bin/env python3
"""Post-process the M2 World Problems deck.

No timer plugin is used in this deck. This script only injects the
Cache-Control: no-store meta tags so the browser always re-fetches the
document and its linked assets. Idempotent: safe to re-run after every render.
"""
import sys

SLIDE_DIR = "PROJECTS/M3 VOCAB/slides"
path = f"{SLIDE_DIR}/index.html"
h = open(path, encoding="utf-8").read()
orig = h

# Cache-Control: no-store meta tags (browser always re-fetches doc + assets)
if '<meta http-equiv="Cache-Control"' not in h:
    h = h.replace(
        '<meta name="viewport"',
        '<meta http-equiv="Cache-Control" content="no-store, no-cache">\n  '
        '<meta http-equiv="Pragma" content="no-cache">\n  '
        '<meta name="viewport"',
    )

if h == orig:
    print("No changes applied — deck already post-processed?")
else:
    open(path, "w", encoding="utf-8").write(h)
    print("Post-processing complete")
