from __future__ import annotations

import html as html_mod
from typing import Optional


# ── Backgrounds ──────────────────────────────────────────────────────────

def slide_bg(
    color: Optional[str] = None,
    gradient: Optional[str] = None,
    image: Optional[str] = None,
    size: Optional[str] = None,
    position: Optional[str] = None,
    repeat: Optional[str] = None,
    opacity: Optional[float] = None,
    video: Optional[str] = None,
    video_loop: bool = False,
    video_muted: bool = True,
    iframe: Optional[str] = None,
    iframe_interactive: bool = False,
    transition: Optional[str] = None,
) -> str:
    parts = []
    _attr("data-background-color", color, parts)
    _attr("data-background-gradient", gradient, parts)
    _attr("data-background-image", image, parts)
    _attr("data-background-size", size, parts)
    _attr("data-background-position", position, parts)
    _attr("data-background-repeat", repeat, parts)
    if opacity is not None:
        parts.append(f'data-background-opacity="{opacity}"')
    _attr("data-background-video", video, parts)
    if video_loop:
        parts.append('data-background-video-loop')
    if video_muted and video:
        parts.append('data-background-video-muted')
    _attr("data-background-iframe", iframe, parts)
    if iframe_interactive and iframe:
        parts.append('data-background-iframe-interactive')
    _attr("data-background-transition", transition, parts)
    return " ".join(parts)


# ── Auto-Animate ─────────────────────────────────────────────────────────

def auto_animate_pair(
    slide1: str,
    slide2: str,
    easing: Optional[str] = None,
    duration: Optional[float] = None,
    delay: Optional[float] = None,
    unmatched: Optional[str] = None,
    restart: bool = False,
) -> str:
    first_attrs = 'data-auto-animate'
    if restart:
        first_attrs += ' data-auto-animate-restart'
    easing_str = f' data-auto-animate-easing="{easing}"' if easing else ''
    duration_str = f' data-auto-animate-duration="{duration}"' if duration else ''
    delay_str = f' data-auto-animate-delay="{delay}"' if delay else ''
    unmatched_str = f' data-auto-animate-unmatched="{unmatched}"' if unmatched else ''
    first = f'<section {first_attrs}{easing_str}{duration_str}{delay_str}{unmatched_str}>'
    second = f'<section data-auto-animate>'
    return first + slide1 + '</section>' + second + slide2 + '</section>'


def auto_animate_attrs(
    easing: Optional[str] = None,
    duration: Optional[float] = None,
    delay: Optional[float] = None,
    unmatched: Optional[str] = None,
    restart: bool = False,
) -> str:
    parts = ['data-auto-animate']
    if restart:
        parts.append('data-auto-animate-restart')
    _attr("data-auto-animate-easing", easing, parts)
    if duration is not None:
        parts.append(f'data-auto-animate-duration="{duration}"')
    if delay is not None:
        parts.append(f'data-auto-animate-delay="{delay}"')
    _attr("data-auto-animate-unmatched", unmatched, parts)
    return " ".join(parts)


# ── Transitions ──────────────────────────────────────────────────────────

_TRANSITIONS = {"slide", "fade", "convex", "concave", "zoom", "none"}

def slide_transition(
    transition: Optional[str] = None,
    speed: Optional[str] = None,
    bg_transition: Optional[str] = None,
) -> str:
    parts = []
    if transition and transition in _TRANSITIONS:
        parts.append(f'data-transition="{transition}"')
    if speed in ("fast", "slow"):
        parts.append(f'data-transition-speed="{speed}"')
    if bg_transition and bg_transition in _TRANSITIONS:
        parts.append(f'data-background-transition="{bg_transition}"')
    return " ".join(parts)


# ── Slide Visibility ─────────────────────────────────────────────────────

def slide_visibility(hidden: bool = False, uncounted: bool = False) -> str:
    if hidden:
        return 'data-visibility="hidden"'
    if uncounted:
        return 'data-visibility="uncounted"'
    return ""


# ── Auto-Slide ───────────────────────────────────────────────────────────

def auto_slide(ms: int) -> str:
    return f'data-autoslide="{ms}"'


# ── Markup / States ──────────────────────────────────────────────────────

def slide_state(state: str) -> str:
    return f'data-state="{html_mod.escape(state)}"'


# ── Vertical Slides ──────────────────────────────────────────────────────

def vertical_slides(*slides: str) -> str:
    return "<section>" + "\n".join(slides) + "</section>"


def navigation_mode(mode: str = "default") -> str:
    return f'data-navigation-mode="{mode}"'


# ── Links ────────────────────────────────────────────────────────────────

def slide_link(anchor: str) -> str:
    return f'href="#/{anchor.lstrip("#/")}"'


def nav_button(direction: str) -> str:
    valid = {"prev", "next", "up", "down"}
    d = direction if direction in valid else "next"
    return f'class="navigate-{d}"'


def preview_link(enabled: bool = True) -> str:
    if enabled:
        return 'data-preview-link'
    return 'data-preview-link="false"'


# ── Code ─────────────────────────────────────────────────────────────────

def code_block(
    code: str,
    language: Optional[str] = None,
    trim: bool = True,
    noescape: bool = False,
    line_numbers: Optional[str] = None,
    ln_start: Optional[int] = None,
    highlights: Optional[str] = None,
    step_highlights: Optional[str] = None,
) -> str:
    attrs = []
    if language:
        attrs.append(f'class="language-{html_mod.escape(language)}"')
    if trim:
        attrs.append("data-trim")
    if noescape:
        attrs.append("data-noescape")
    if line_numbers:
        attrs.append(f'data-line-numbers="{html_mod.escape(line_numbers)}"')
    if ln_start is not None:
        attrs.append(f'data-ln-start-from="{ln_start}"')
    if highlights:
        attrs.append(f'data-highlight="{html_mod.escape(highlights)}"')
    if step_highlights:
        attrs.append(f'data-step-highlights="{html_mod.escape(step_highlights)}"')
    attr_str = " " + " ".join(attrs) if attrs else ""
    escaped_code = html_mod.escape(code)
    return f"<pre><code{attr_str}>{escaped_code}</code></pre>"


# ── Media ────────────────────────────────────────────────────────────────

def video_embed(src: str, autoplay: bool = True, preload: bool = False, ignore: bool = False) -> str:
    return _media_element("video", src, autoplay, preload, ignore)


def audio_embed(src: str, autoplay: bool = True, preload: bool = False, ignore: bool = False) -> str:
    return _media_element("audio", src, autoplay, preload, ignore)


def iframe_embed(src: str, autoplay: bool = True, preload: bool = False, ignore: bool = False) -> str:
    return _media_element("iframe", src, autoplay, preload, ignore)


def _media_element(tag: str, src: str, autoplay: bool, preload: bool, ignore: bool) -> str:
    attrs = [f'data-src="{html_mod.escape(src)}"']
    if autoplay:
        attrs.append("data-autoplay")
    if preload:
        attrs.append("data-preload")
    if ignore:
        attrs.append("data-ignore")
    attr_str = " ".join(attrs)
    return f"<{tag} {attr_str}></{tag}>"


# ── Lightbox ─────────────────────────────────────────────────────────────

def preview_image(url: str) -> str:
    return f'data-preview-image="{html_mod.escape(url)}"'


def preview_video(url: str) -> str:
    return f'data-preview-video="{html_mod.escape(url)}"'


def preview_link(url: str, fit: bool = False) -> str:
    attrs = [f'data-preview-link="{html_mod.escape(url)}"']
    if fit:
        attrs.append('data-preview-fit')
    return " ".join(attrs)


# ── Layout ───────────────────────────────────────────────────────────────

def stack(*children: str) -> str:
    inner = "\n".join(children)
    return f'<div class="r-stack">{inner}</div>'


def fit_text(text: str) -> str:
    return f'<h2 class="r-fit-text">{html_mod.escape(text)}</h2>'


def stretch(content: str) -> str:
    return f'<div class="r-stretch">{content}</div>'


def frame(*children: str) -> str:
    inner = "\n".join(children)
    return f'<div class="r-frame">{inner}</div>'


# ── Generic ──────────────────────────────────────────────────────────────

def html_attrs(**kwargs) -> str:
    return " ".join(f'data-{k}="{html_mod.escape(str(v))}"' for k, v in kwargs.items())


# ── Internal helpers ─────────────────────────────────────────────────────

def _attr(name: str, value: Optional[str], parts: list[str]) -> None:
    if value:
        parts.append(f'{name}="{html_mod.escape(value)}"')
