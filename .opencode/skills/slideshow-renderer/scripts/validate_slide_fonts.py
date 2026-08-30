"""
validate_slide_fonts.py — Check data.json for gray fonts and undersized text.

Usage:
    python validate_slide_fonts.py path/to/data.json

Exit codes:
    0 — all clear
    1 — violations found
"""

import json
import re
import sys
from typing import Any


GRAY_NAMED = {"gray", "grey", "lightgray", "lightgrey", "darkgray", "darkgrey", "silver", "gainsboro", "dimgray", "dimgrey"}

_GRAY_VALUES = {0x88, 0x99, 0x9a, 0x9b, 0x9c, 0xaa, 0xab, 0xac, 0xad, 0xae, 0xaf, 0xbb, 0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbc, 0xbd, 0xbe, 0xbf, 0xcc, 0xcd, 0xce, 0xcf, 0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xdb, 0xdc, 0xdd}


def _is_gray_hex(hex_color: str) -> bool:
    """Check if a hex color like #888 or #aabbcc is gray (R≈G≈B in 0x88-0xdd)."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        r = int(h[0] * 2, 16)
        g = int(h[1] * 2, 16)
        b = int(h[2] * 2, 16)
    elif len(h) == 6:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
    else:
        return False
    # Check for gray (R≈G≈B) with values in the 0x88-0xdd mid-gray range
    if abs(r - g) > 8 or abs(g - b) > 8 or abs(r - b) > 8:
        return False
    return r in _GRAY_VALUES and g in _GRAY_VALUES and b in _GRAY_VALUES


def _scan_text(text: str, violations: list[str], context: str) -> None:
    if not isinstance(text, str):
        return

    # Check font sizes
    for m in re.finditer(r'font-size\s*:\s*(\d+)', text, re.IGNORECASE):
        size = int(m.group(1))
        if size < 28:
            violations.append(f"[{context}] font-size: {size}px (minimum is 28px): ...{text[max(0, m.start()-30):m.end()+30]}...")

    # Check gray-named colors
    for m in re.finditer(r'color\s*:\s*(' + '|'.join(GRAY_NAMED) + r')\b', text, re.IGNORECASE):
        violations.append(f"[{context}] gray font color '{m.group(1)}': ...{text[max(0, m.start()-30):m.end()+30]}...")

    # Check gray hex colors
    for m in re.finditer(r'color\s*:\s*(#[0-9a-fA-F]{3,8})', text):
        hex_val = m.group(1)
        if _is_gray_hex(hex_val):
            violations.append(f"[{context}] gray font color {hex_val}: ...{text[max(0, m.start()-30):m.end()+30]}...")


def validate(data: dict) -> list[str]:
    violations: list[str] = []

    deck_title = data.get("title", "untitled")
    slides = data.get("slides", [])

    for i, slide in enumerate(slides):
        sid = slide.get("id", f"slide-{i+1}")
        prefix = f"slide {i+1} (id={sid})"
        _scan_text(slide.get("title", ""), violations, f"{prefix}/title")
        _scan_text(slide.get("body", ""), violations, f"{prefix}/body")
        _scan_text(slide.get("notes", ""), violations, f"{prefix}/notes")
        for fi, frag in enumerate(slide.get("fragments", [])):
            _scan_text(frag, violations, f"{prefix}/fragment[{fi}]")

    return violations


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python validate_slide_fonts.py path/to/data.json", file=sys.stderr)
        return 1

    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    violations = validate(data)
    if violations:
        print(f"Found {len(violations)} violation(s):\n")
        for v in violations:
            print(f"  - {v}")
        return 1
    else:
        print("All fonts OK — no gray colors or undersized text.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
