from __future__ import annotations

import html as html_mod
import markdown
from typing import Optional


_FRAGMENT_STYLES = {
    "fade", "fade-up", "fade-down", "fade-left", "fade-right",
    "fade-in-then-out", "fade-in-then-semi-out",
    "grow", "semi-fade", "shrink", "strike",
    "highlight-red", "highlight-green", "highlight-blue",
    "highlight-current-red", "highlight-current-green", "highlight-current-blue",
    "fade-out", "fade-out-up", "fade-out-down", "fade-out-left", "fade-out-right",
}


def fragment(
    content: str,
    style: Optional[str] = None,
    index: Optional[int] = None,
) -> str:
    classes = ["fragment"]
    if style and style in _FRAGMENT_STYLES:
        classes.append(style)
    class_str = " ".join(classes)
    attrs = f'class="{class_str}"'
    if index is not None:
        attrs += f' data-fragment-index="{index}"'
    return f'<span {attrs}>{content}</span>'


def notes(text: str) -> str:
    return f"<aside class=\"notes\">{html_mod.escape(text)}</aside>"


def markdown_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=["extra"])
