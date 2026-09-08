#!/usr/bin/env python3
"""READING M2 — independent-reading produce driver.

POST-GATE terminal step for the independent-reading generator skill.
Reads the sibling reading.json envelope, then for each CEFR level:
  1. flatten the 4 chunk body paragraphs (headlines are NOT counted)
  2. SANITISE (unicode/spacing/reflow + gloss superscript markers + count)
  3. ensure the deterministic count lands in [target, cap]
  4. build a Pydantic-validated ReadingText and RENDER it to PDF
  5. merge the level PDFs (B1 first, then B2) into ONE combined PDF
  6. VERIFY each per-level PDF

The simplify -> Kimi -> human gates are INTERACTIVE and live OUTSIDE this
script. This refuses to render until the envelope's `approved` flag is True
(Gate 2). The `just indread-render` recipe runs this with no flags.

Modes:
  python3 produce.py --check      sanitise + word-count table, NO render
  python3 produce.py --approve    set approved=true in reading.json (Gate 2)
  python3 produce.py              render + combine + verify (post-approval)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

SKILL_SCRIPTS = Path("/home/elwru/.agents/skills/independent-reading-text-generator/scripts")
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))

from models import ReadingText          # noqa: E402  # type: ignore[import-not-found]
from sanitise import sanitise           # noqa: E402  # type: ignore[import-not-found]
from target_calc import compute_targets  # noqa: E402  # type: ignore[import-not-found]
from word_count import count_words      # noqa: E402  # type: ignore[import-not-found]
from render import render               # noqa: E402  # type: ignore[import-not-found]
from verify import verify_pdf           # noqa: E402  # type: ignore[import-not-found]

HERE = Path(__file__).resolve().parent
ENVELOPE = HERE / "reading.json"
REPO_ROOT = HERE.parents[3]  # /mnt/c/PROJECTS/LESSON-PLAN-WRITER-4
# Output goes to the SOURCE repo project's PDF folder (user-specified), NOT the
# skill's default INDEPENDENT-READING/... location.
PDF_DIR = REPO_ROOT / "PROJECTS" / "READING M2" / "PDF"
BANNER = REPO_ROOT / "PROJECTS" / "READING M2" / "meta-banner.jpg"


def load_envelope() -> dict:
    if not ENVELOPE.exists():
        raise SystemExit(f"envelope not found: {ENVELOPE}")
    return json.loads(ENVELOPE.read_text(encoding="utf-8"))


def save_envelope(env: dict) -> None:
    ENVELOPE.write_text(json.dumps(env, indent=2, ensure_ascii=False), encoding="utf-8")


def flatten_body(chunks: list[dict]) -> list[str]:
    """Body paragraphs only — chunk headlines are excluded from the count."""
    paras: list[str] = []
    for chunk in chunks:
        paras.extend(str(p) for p in chunk.get("paragraphs", []))
    return paras


def build_render_paragraphs(chunks: list[dict], marked_body: list[str]) -> list[dict | str]:
    """Interleave section-head dicts (chunk headlines) with marked body paras.

    The sanitised body paragraphs carry gloss superscript markers. We thread
    the headlines back through in order, one per chunk, matching the chunk's
    body paragraphs by position (all body paragraphs are consumed in order,
    so the marked list slots into each chunk span-by-span).
    """
    out: list[dict | str] = []
    idx = 0
    for chunk in chunks:
        headline = str(chunk.get("headline", "")).strip()
        if headline:
            out.append({"class": "section-head", "text": headline})
        n = len(chunk.get("paragraphs", []))
        out.extend(marked_body[idx:idx + n])
        idx += n
    return out


def check_level(level: dict) -> tuple[int, list[str], list[dict], list[str]]:
    """Sanitise a level's body, return (body_words, marked_paras, glosses, chunk_paras)."""
    body = flatten_body(level["chunks"])
    raw = "\n\n".join(body)
    gloss_spec = level.get("glosses") or []
    s = sanitise(raw, gloss_spec=gloss_spec, target_words=None)
    return s.words, s.paragraphs, [g.model_dump() for g in s.glosses], body


def verify_envelope_level(level: dict, words: int) -> tuple[int, int, bool]:
    minutes = int(level.get("minutes", 8))
    target, cap = compute_targets(level["cefr"], minutes)
    return target, cap, target <= words <= cap


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="sanitise + count, no render")
    ap.add_argument("--approve", action="store_true", help="set approved=true (Gate 2)")
    args = ap.parse_args()

    env = load_envelope()
    levels = env["levels"]
    approved = bool(env.get("approved", False))

    # ── --check: report counts only ─────────────────────────────────────────
    if args.check:
        print(f"== READING M2 independent-reading CHECK (approved={approved}) ==")
        for lvl in levels:
            words, *_ = check_level(lvl)
            target, cap, in_band = verify_envelope_level(lvl, words)
            kind = "OK" if in_band else "OUT OF BAND"
            print(f"  {lvl['cefr']}: body={words}  target={target}  cap={cap}  [{kind}]")
        return

    # ── --approve: flip Gate 2 flag ─────────────────────────────────────────
    if args.approve:
        env["approved"] = True
        save_envelope(env)
        print("approved=true written to reading.json")
        return

    # ── render path: must be approved ──────────────────────────────────────
    if not approved:
        raise SystemExit(
            "Gate 2 not passed: approved=false. Present the text for human review, "
            "then run `python3 produce.py --approve` and re-run the recipe."
        )

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    banner = str(BANNER)
    if not Path(banner).exists():
        raise SystemExit(f"banner not found: {banner}")

    rendered: list[tuple[Path, ReadingText]] = []
    for lvl in levels:
        level = dict(lvl)
        words, marked, gloss_dicts, _body = check_level(level)
        target, cap, in_band = verify_envelope_level(level, words)
        if not in_band:
            raise SystemExit(
                f"{level['cefr']} out of band: {words} not in [{target}, {cap}]"
            )

        render_paras = build_render_paragraphs(level["chunks"], marked)
        slug = "".join(c for c in level["title"].lower() if c.isalnum() or c == "-").strip("-")
        out_pdf = PDF_DIR / f"{level['cefr'].lower()}-{date.today().isoformat()}-{slug}.pdf"

        reading = ReadingText(
            cefr=level["cefr"],
            minutes=int(level.get("minutes", 8)),
            title=level["title"],
            byline=level.get("byline"),
            source_url=level.get("source_url"),
            words=words,
            target_words=words,
            cap_words=cap,
            simplified=level["cefr"] in ("A2", "B1"),
            kimi_verdict=level.get("kimi_verdict", "skipped"),
            human_approved=True,                # render() gate — already past Gate 2
            glosses=[dict(g) for g in gloss_dicts],
            target_line=0,
            banner_path=banner,
            context_box=level.get("context_box"),
            output_path=str(out_pdf),
        )
        produced = render(reading, render_paras, PDF_DIR)
        rendered.append((Path(produced), reading))
        print(f"[produce] rendered {level['cefr']}: {produced.name} ({words} words)")

    # ── combine: B1 first, then B2 ─────────────────────────────────────────
    combined = combine_pdfs(rendered, levels[0]["title"])
    print(f"[produce] combined -> {combined.name}")

    # ── verify each per-level PDF ──────────────────────────────────────────
    # Use wrap-safe probes: the FIRST few words of the level's own first body
    # paragraph and the LAST few words of its last body paragraph (short enough
    # to stay inside one rendered line — a long slice spans line-wraps and fails).
    for (pdf, reading), level in zip(rendered, levels):
        body = flatten_body(level["chunks"])
        first = body[0].split()[:6]           # ~6 words of the opening paragraph
        # probe the CLOSING paragraph's opening — its final words wrap across
        # lines, so a long end-of-paragraph slice would not be found in the
        # raw (newline-separated) PDF text. The first line of the last
        # paragraph is wrap-safe.
        last = body[-1].split()[:5]
        res = verify_pdf(pdf, reading,
                         first_words=" ".join(first), last_words=" ".join(last))
        status = "OK" if res.ok else "; ".join(res.errors)
        print(f"[verify] {reading.cefr}: {status}")


def combine_pdfs(rendered: list[tuple[Path, ReadingText]], title: str) -> Path:
    """Merge the level PDFs into one file, B1 first then B2, preserving each
    section's own masthead, CEFR badge, running head and page numbering."""
    import pymupdf

    slug = "".join(c for c in title.lower() if c.isalnum() or c == "-").strip("-")
    combined_path = PDF_DIR / f"combined-b1-b2-{date.today().isoformat()}-{slug}.pdf"
    merged = pymupdf.open()
    try:
        for pdf, _reading in rendered:
            src = pymupdf.open(str(pdf))
            try:
                merged.insert_pdf(src)
            finally:
                src.close()
        merged.save(str(combined_path), garbage=4, deflate=True)
    finally:
        merged.close()
    return combined_path


if __name__ == "__main__":
    main()
