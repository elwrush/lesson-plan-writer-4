# Jinja2 Macro Contracts

## Output format

Every macro returns a string of HTML suitable for insertion inside `<div class="slides">` — one or more `<section>` elements.

## `{% macro render_content_slide(slide) %}`

**Layout**: `content`

Renders a single `<section>` with title and body.

- `slide.title` → markdown-rendered via `markdown_to_html` filter, wrapped in `<h2>` unless empty (renders `<h2></h2>`)
- `slide.body` → markdown-rendered content via `markdown_to_html` filter, wrapped in `<div>` unless empty (renders empty `<div></div>`)
- `slide.notes` → hidden `<aside class="notes">`, markdown-rendered via `markdown_to_html` filter
- `slide.auto_animate` → if true, adds `data-auto-animate` to `<section>`
- `slide.data_id` → `data-id` on `<section>` (for auto-animate cross-referencing)
- `slide.fragment_index` → `data-fragment-index` on section

## `{% macro render_two_column_slide(slide) %}`

**Layout**: `two-column`

Renders a single `<section>` with a left/right split.

- `slide.body` split on `|||` → left column / right column
- Each column rendered as markdown inside `<div class="col">`
- Uses `slideshow_lib.stretch()` to fill available space

## `{% macro render_auto_animate_pair(group) %}`

**Layout**: `auto-animate-pair`

Renders two (or more) `<section>` elements with matching `data-auto-animate` attributes.

- `group` is a list of slides sharing the same `id`, ordered by `step`
- First slide gets `data-auto-animate` with optional `data-auto-animate-restart`
- Each subsequent slide gets `data-auto-animate`
- Inner elements with matching `data-id` morph between slides
- `slideshow_lib.auto_animate_attrs()` generates the per-section attribute string

## `{% macro render_code_slide(slide) %}`

**Layout**: `code`

Renders a single `<section>` with a code block.

- `slide.title` → `<h2>` (optional)
- `slide.code` → rendered via `slideshow_lib.code_block(slide.code, language=slide.language)`
- Syntax highlight class added via `language-{lang}`

## `{% macro render_image_slide(slide) %}`

**Layout**: `image`

Renders a single `<section>` with an image as background or inline.

- `slide.image_url` → `data-background-image` attribute via `slideshow_lib.slide_bg()`
- `slide.title` overlaid as `<h2>` with `r-fit-text` class

## `{% macro render_raw_slide(slide) %}`

**Layout**: `raw`

Passthrough — `slide.body` is inserted verbatim into a bare `<section>`.

- Resolver assigns `fragment_index` and `data_id` for structural consistency
- No auto-animate attributes, no `element_ids` assigned
- Content is NOT markdown-processed — inserted verbatim
- No validation of the content (broken HTML passes through)
- Wrapped in `<section>` for structural consistency only
