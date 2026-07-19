from .globals import (
    slide_bg,
    auto_animate_pair,
    auto_animate_attrs,
    slide_transition,
    slide_visibility,
    auto_slide,
    slide_state,
    vertical_slides,
    slide_link,
    nav_button,
    preview_link,
    code_block,
    video_embed,
    audio_embed,
    iframe_embed,
    preview_image,
    preview_video,
    stack,
    fit_text,
    stretch,
    frame,
    html_attrs,
)
from .filters import fragment, notes, markdown_to_html


def setup_jinja(env):
    for name, fn in _globals().items():
        env.globals[name] = fn
    for name, fn in _filters().items():
        env.filters[name] = fn


def _globals():
    return {
        "slide_bg": slide_bg,
        "auto_animate_pair": auto_animate_pair,
        "auto_animate_attrs": auto_animate_attrs,
        "slide_transition": slide_transition,
        "slide_visibility": slide_visibility,
        "auto_slide": auto_slide,
        "slide_state": slide_state,
        "vertical_slides": vertical_slides,
        "slide_link": slide_link,
        "nav_button": nav_button,
        "preview_link": preview_link,
        "code_block": code_block,
        "video_embed": video_embed,
        "audio_embed": audio_embed,
        "iframe_embed": iframe_embed,
        "preview_image": preview_image,
        "preview_video": preview_video,
        "stack": stack,
        "fit_text": fit_text,
        "stretch": stretch,
        "frame": frame,
        "html_attrs": html_attrs,
    }


def _filters():
    return {
        "fragment": fragment,
        "notes": notes,
        "markdown_to_html": markdown_to_html,
    }
