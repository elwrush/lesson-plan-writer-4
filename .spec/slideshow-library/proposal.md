## Proposal: slideshow-library

## What
Build a reusable Python library that Jinja2 can access when rendering reveal.js slideshows. The library lives at `~/.kilo/skills/slideshow-renderer/lib/` and exposes Jinja2 filters, globals, and tests via a single `setup_jinja(env)` entry point.

The library's purpose: **wrap every reveal.js data-attribute, class, and HTML pattern so templates never need to memorize the API**. Instead of remembering whether it's `data-background-color` or `data-bg-color`, or whether fragment styles go in `class="fragment highlight-red"` or as separate attributes, template authors call named Python functions.

All functions draw directly from the official docs at `https://revealjs.com/`.

## Feature map (by reveal.js doc page)

| Doc page | Helpers |
|---|---|
| **[Backgrounds](/backgrounds/)** | `slide_bg()` → `data-background-color`, `data-background-gradient`, `data-background-image`, `data-background-size/position/repeat/opacity`, `data-background-video` (+loop/muted), `data-background-iframe` (+interactive), `data-background-transition` |
| **[Fragments](/fragments/)** | `fragment()` filter → `class="fragment [style]"` for all 20+ built-in styles, `fragment_index()` for `data-fragment-index`, nested fragments, custom fragments |
| **[Auto-Animate](/auto-animate/)** | `auto_animate_pair()` → paired `<section data-auto-animate>` blocks with matching `data-id` elements, `auto_animate_attrs()` for individual element settings (easing, duration, delay, unmatched, id, restart) |
| **[Transitions](/transitions/)** | `slide_transition()` → `data-transition`, `data-transition-speed`, `data-background-transition`, in/out variants |
| **[Slide Visibility](/slide-visibility/)** | `slide_visibility()` → `data-visibility="hidden"` / `"uncounted"` |
| **[Auto-Slide](/auto-slide/)** | `auto_slide()` → `data-autoslide` |
| **[Speaker View](/speaker-view/)** | `notes()` filter → `<aside class="notes">`, `data_timing()` for `data-timing` |
| **[Markup](/markup/)** (states) | `slide_state()` → `data-state` |
| **[Vertical Slides](/vertical-slides/)** | `vertical_slides()` → wraps multiple sections in a vertical stack parent, `navigation_mode()` for config |
| **[Links](/links/)** | `slide_link()` → `#/id` or `#/0/0` format, `nav_button()` → `class="navigate-*"`, `preview_link()` → `data-preview-link` |
| **[Code](/code/)** | `code_block()` → complete `<pre><code>` with `data-trim`, `data-noescape`, `data-line-numbers`, `data-ln-start-from`, step-by-step highlights, language class |
| **[Media](/media/)** | `video_embed()`, `audio_embed()`, `iframe_embed()` → elements with `data-autoplay`, `data-src` lazy loading, `data-preload`, `data-ignore` |
| **[Lightbox](/lightbox/)** | `preview_image()`, `preview_video()`, `preview_link()` → `data-preview-image`, `data-preview-video`, `data-preview-link`, `data-preview-fit` |
| **[Layout](/layout/)** | `stack()`, `fit_text()`, `stretch()`, `frame()` → class helpers `r-stack`, `r-fit-text`, `r-stretch`, `r-frame` |
| **Generic** | `html_attrs(**kwargs)` → escape hatch for any `data-*` attribute not in the named list |

## Why
- reveal.js has 40+ data-* attributes spread across 15+ doc pages. Memorizing them is error-prone — wrong attribute names, wrong argument order, wrong HTML nesting
- Fragments alone have 20+ style classes with specific naming conventions (`fade-in-then-out`, `highlight-current-red`)
- Auto-animate requires paired slides with matching content structure — a single mismatched `data-id` breaks the animation
- Code blocks need 5+ attributes for proper syntax highlighting
- A library means template authors (and LLM agents writing templates) call `fragment("text", style="highlight-red")` instead of constructing `<span class="fragment highlight-red">text</span>` by hand
- Each function is a standalone, testable Python function — not template logic

## Done
- `~/.kilo/skills/slideshow-renderer/lib/slideshow_lib/` exists with `setup_jinja(env)` entry point
- All 14 doc-page categories implemented as Jinja2 filters/globals
- Every function has a red-green test pair verifying both the error case (filter not registered) and the correct output
- `fragment("text", style="highlight-red")` → `<span class="fragment highlight-red">text</span>`
- `slide_bg(color="#09b", gradient="radial-gradient(...)")` → `data-background-color="#09b" data-background-gradient="radial-gradient(...)"`
- `auto_animate_pair(slide1, slide2, duration=0.8)` → two `<section data-auto-animate>` elements
- `code_block("def f(): pass", language="python", line_numbers="3,8-10")` → complete `<pre><code>` structure
- `notes("check comprehension")` → `<aside class="notes">check comprehension</aside>`
- `html_attrs(auto_animate_easing="ease-out")` → `data-auto-animate-easing="ease-out"`
- All valid style names, transition names, etc. validated against enums derived from reveal.js docs
- 100% test coverage on all public functions
- Importable via `sys.path.insert(0, expanduser("~/.kilo/skills/slideshow-renderer/lib"))`
- No files created outside `~/.kilo/skills/slideshow-renderer/lib/`

## Constraints
- No new files in this repo (LPW-4) — only `~/.kilo/skills/slideshow-renderer/lib/`
- Zero runtime dependencies beyond `jinja2` and stdlib
- Functions return strings or dicts of attributes — they don't write to any output
- No knowledge of lesson shapes, lesson plans, or pedagogical models
- Must not mutate the `Environment` it's given
- Must not depend on any Kilo CLI internals
- Valid style/transition names come from reveal.js docs, maintained as enums in the library
- HTML output must be context-appropriate (attribute values quoted, content escaped where needed)
