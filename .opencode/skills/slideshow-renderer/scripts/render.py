#!/usr/bin/env python3
"""Render a layout-driven slide deck from data.json + macros.jinja2 → index.html."""

import argparse
import json
import sys
import re
from pathlib import Path
from typing import Iterator, Optional

import jinja2
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Literal

# ── Library import ───────────────────────────────────────────────────────
SKILL_DIR = Path(__file__).resolve().parent.parent
LIB_DIR = SKILL_DIR / "lib"
sys.path.insert(0, str(LIB_DIR))
from slideshow_lib import setup_jinja


# ── Pydantic models ─────────────────────────────────────────────────────

LayoutType = Literal["content", "two-column", "auto-animate-pair", "code", "image", "raw"]


class SlideRecord(BaseModel):
    layout: LayoutType
    id: str = Field(..., min_length=1)
    step: int = Field(default=1, ge=1)
    title: str = ""
    body: str = ""
    notes: str = ""
    image_url: str = ""
    code: str = ""
    language: str = ""
    media: dict = Field(default_factory=dict)
    fragment_order: Optional[int] = None
    background_color: str = ""
    background_image: str = ""
    fragments: list[str] = Field(default_factory=list)
    shield: bool = False
    logo: str = ""
    cta: str = ""

    @model_validator(mode="after")
    def check_content(self):
        if self.layout != "raw" and not self.title and not self.body and not self.code and not self.image_url and not self.background_image:
            raise ValueError("At least one of title, body, code, image_url, background_image must be non-empty")
        return self


class DeckData(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = ""
    theme: str = "white"
    transition: str = "slide"
    slides: list[SlideRecord]


class ResolvedSlide(BaseModel):
    layout: LayoutType
    id: str
    step: int
    title: str = ""
    body: str = ""
    notes: str = ""
    image_url: str = ""
    code: str = ""
    language: str = ""
    media: dict = Field(default_factory=dict)
    fragment_order: Optional[int] = None
    background_color: str = ""
    background_image: str = ""
    fragments: list[str] = Field(default_factory=list)
    shield: bool = False
    logo: str = ""
    cta: str = ""
    data_id: str = ""
    element_ids: dict[str, str] = Field(default_factory=dict)
    auto_animate: bool = False
    auto_animate_group_id: Optional[str] = None
    fragment_index: int = 1


# ── Resolver ─────────────────────────────────────────────────────────────

def _sanitize_id(raw: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "-", raw).strip("-") or "slide"


def resolve_deck(data: dict) -> dict:
    slides = data.get("slides", [])
    groups: dict[str, list[dict]] = {}
    for s in slides:
        gid = s.get("id", "slide")
        groups.setdefault(gid, []).append(s)

    resolved: list[ResolvedSlide] = []
    frag_idx = 1

    for s in slides:
        gid = s.get("id", "slide")
        group = groups[gid]
        group_size = len(group)
        sanitized = _sanitize_id(gid)

        auto_animate = group_size >= 2
        auto_animate_group_id = f"group-{sanitized}" if auto_animate else None

        element_ids: dict[str, str] = {}
        if auto_animate and s.get("layout") != "raw":
            element_ids = {
                "title": f"el-{sanitized}-title",
                "body": f"el-{sanitized}-body",
            }

        data_id = f"slide-{sanitized}-{s.get('step', 1)}"

        resolved.append(ResolvedSlide(
            layout=s["layout"],
            id=gid,
            step=s.get("step", 1),
            title=s.get("title", ""),
            body=s.get("body", ""),
            notes=s.get("notes", ""),
            image_url=s.get("image_url", ""),
            code=s.get("code", ""),
            language=s.get("language", ""),
            media=s.get("media", {}),
            fragment_order=s.get("fragment_order"),
            background_color=s.get("background_color", ""),
            background_image=s.get("background_image", ""),
            fragments=s.get("fragments", []),
            shield=s.get("shield", False),
            logo=s.get("logo", ""),
            cta=s.get("cta", ""),
            data_id=data_id,
            element_ids=element_ids,
            auto_animate=auto_animate,
            auto_animate_group_id=auto_animate_group_id,
            fragment_index=frag_idx,
        ))
        frag_idx += 1

    return {
        "title": data.get("title", ""),
        "author": data.get("author", ""),
        "theme": data.get("theme", "white"),
        "transition": data.get("transition", "slide"),
        "slides": [r.model_dump() for r in resolved],
    }


# ── CDN skeleton ─────────────────────────────────────────────────────────

CDN_SKELETON = """\
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reset.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/{theme}.css" id="theme">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/monokai.css">
  <style>
    .reveal .shield{{display:flex;align-items:center;width:fit-content;margin:0.6em auto;padding:0.1em 0.4em;background:rgba(0,0,0,0.55);border-radius:4px;text-shadow:none;line-height:1.3}}.reveal .cta-text{{color:#ffdd00;font-size:1.3em;font-weight:700}}.box-word{{display:inline-block;border:2px solid #ffdd00;border-radius:4px;padding:1px 7px;font-weight:700;color:#ffdd00}}.reveal .slides section{{padding:0 8px !important}}.reveal .slides section h2{{font-size:44px !important;width:100%;margin-left:auto;margin-right:auto}}.reveal .slides section > div:not(.shield):not(.cta-box):not(.title-logo-wrap){{width:100%;margin-left:auto;margin-right:auto}}.reveal .title-logo{{display:inline}}.cta-box{{display:inline-block;border:2px solid #ffdd00;border-radius:6px;padding:0.6em 1.2em;margin:1em auto;text-align:center}}.cta-box p{{color:#ffdd00;font-weight:700;font-size:1.2em;margin:0}}.fragment{{transition:all 0.2s ease}}.vocab-phon{{color:#fff;font-size:1em;font-style:italic}}.vocab-ctx{{color:#fff;font-size:1em;font-style:italic;max-width:700px;line-height:1.5}}.video-box{{width:95%;max-width:900px;margin:0 auto;aspect-ratio:16/9}}.video-box iframe{{width:100%;height:100%;border:none}}.strategy-label{{color:#ffdd00;font-size:0.85em;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5em}}.q-block{{border-left:3px solid #ffdd00;padding-left:1em;margin:1em 0;text-align:left}}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
{slides}
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/notes/notes.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/highlight.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/search/search.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/zoom/zoom.js"></script>
  <script>
    Reveal.initialize({{
      controls: true,
      progress: true,
      history: true,
      width: 1280,
      height: 720,
      transition: "{transition}",
      plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]
    }});
  </script>
</body>
</html>"""


# ── Render Pipeline ──────────────────────────────────────────────────────

def _load_macros(env: jinja2.Environment) -> dict:
    tmpl = env.get_template("macros.jinja2")
    module = tmpl.make_module()
    return {
        "content": module.render_content_slide,
        "two-column": module.render_two_column_slide,
        "auto-animate-pair": module.render_auto_animate_pair,
        "code": module.render_code_slide,
        "image": module.render_image_slide,
        "raw": module.render_raw_slide,
    }


def render_deck(data: dict, macros_path: Path) -> str:
    resolved = resolve_deck(data)

    loader = jinja2.FileSystemLoader(str(macros_path.parent))
    env = jinja2.Environment(loader=loader, autoescape=False)
    setup_jinja(env)

    env.filters["strip_p"] = lambda s: s.replace("<p>", "").replace("</p>", "")
    macros = _load_macros(env)
    slides_html_parts: list[str] = []
    seen: set[str] = set()

    for s in resolved["slides"]:
        layout = s["layout"]
        if layout == "auto-animate-pair":
            gid = s["id"]
            if gid not in seen:
                seen.add(gid)
                group = [x for x in resolved["slides"] if x["id"] == gid]
                slides_html_parts.append(macros["auto-animate-pair"](group))
        else:
            slides_html_parts.append(macros[layout](s))

    slides_html = "\n".join(slides_html_parts)

    theme = resolved.get("theme", "white")
    transition = resolved.get("transition", "slide")
    title = resolved.get("title", "Slideshow")

    return CDN_SKELETON.format(
        title=title, theme=theme, transition=transition, slides=slides_html
    )


# ── CLI ──────────────────────────────────────────────────────────────────

def _find_macros() -> Path:
    candidates = [
        SKILL_DIR / "scripts" / "macros.jinja2",
        Path(__file__).parent / "macros.jinja2",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("macros.jinja2 not found")


def main():
    parser = argparse.ArgumentParser(description="Render a reveal.js slideshow from structured data")
    parser.add_argument("--data", "-d", default="data.json", help="Input data JSON (default: data.json)")
    parser.add_argument("--template", "-t", default=None, help="Jinja2 template path (optional, defaults to macros.jinja2)")
    parser.add_argument("--output", "-o", default="slides/index.html", help="Output path (default: slides/index.html)")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Error: data file not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    with open(data_path, encoding="utf-8") as f:
        raw = json.load(f)

    deck = DeckData.model_validate(raw)
    deck_dict = deck.model_dump()

    template_path: Path
    if args.template:
        template_path = Path(args.template)
    else:
        template_path = _find_macros()

    html = render_deck(deck_dict, template_path)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Rendered {len(deck.slides)} slides → {out_path.resolve()}")


if __name__ == "__main__":
    main()
