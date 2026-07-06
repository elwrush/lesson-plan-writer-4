# Data Model: Layout-Driven Slides

## Entities

### LayoutType (enum)

```
content | two-column | auto-animate-pair | code | image | raw
```

Each value maps to exactly one Jinja2 macro in the template.

### SlideRecord

The input data model — what the LLM produces.

| Field | Type | Required | Description |
|---|---|---|---|
| `layout` | `LayoutType` | ✅ | Selects rendering macro |
| `id` | `str` | ✅ | Grouping key for auto-animate pairs. Slides sharing the same `id` form a group. |
| `step` | `int` | ❌ | Sequence position within a group (1-based). Default: 1 if absent. |
| `title` | `str` | ❌ | Markdown text for the slide heading |
| `body` | `str` | ❌ | Markdown text for the slide body content |
| `notes` | `str` | ❌ | Speaker notes (markdown, not displayed on slide) |
| `image_url` | `str` | ❌ | URL or path for background or inline image |
| `code` | `str` | ❌ | Source code (used when `layout=code`) |
| `language` | `str` | ❌ | Programming language for syntax highlighting (used when `layout=code`) |
| `media` | `dict` | ❌ | Optional media embed: `{type: "video"|"audio"|"iframe", src: "...", autoplay: bool}` |
| `fragment_order` | `int` | ❌ | Optional hint for fragment sequencing within the slide |

Validation:
- At least one of `title`, `body`, `code` must be non-empty (unless `layout=raw`). Empty content fields render as empty HTML elements (`<h2></h2>`, `<p></p>`), never omitted.
- When `layout=auto-animate-pair`, the slide must have a matching `id` with exactly one other slide at `step=1` and `step=2`.
- When `layout=two-column`, `body` is split on `|||` delimiter into left/right columns.
- When `layout=code`, `code` field is required and `language` is recommended but optional.

### ResolvedSlide

The output of the resolver — what the Jinja2 macro receives.

| Field | Type | Description |
|---|---|---|
| `layout` | `LayoutType` | Unchanged from input |
| `id` | `str` | Unchanged from input |
| `step` | `int` | Unchanged from input |
| `title` | `str` | Unchanged from input |
| `body` | `str` | Unchanged from input |
| `notes` | `str` | Unchanged from input |
| `image_url` | `str` | Unchanged from input |
| `code` | `str` | Unchanged from input |
| `language` | `str` | Unchanged from input |
| `media` | `dict` | Unchanged from input |
| `fragment_order` | `int` | Unchanged from input |
| `data_id` | `str` | Assigned by resolver. Auto-generated unique id for this slide's section element. Derived from `id` + `step`. |
| `element_ids` | `dict[str, str]` | Assigned by resolver. Mapping of element names to `data-id` values, consistent across grouped slides: `{title: "title-tense", body: "body-tense"}` |
| `auto_animate` | `bool` | Assigned by resolver. `True` when the slide belongs to a group of size >= 2. |
| `auto_animate_group_id` | `str` | Assigned by resolver. Shared across all slides in the same auto-animate group. |
| `fragment_index` | `int` | Assigned by resolver. Globally sequential across the entire deck (1..N). |
| `css_class` | `str` | Assigned by resolver. Stage-based color class: `stage-warmup`, `stage-presentation`, `stage-controlled`, `stage-freer`, `stage-production`. Derived from stage name heuristics. |

### DeckData

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | `str` | ✅ | Slideshow title (used in HTML `<title>` and reveal.js config) |
| `author` | `str` | ❌ | Author name |
| `theme` | `str` | ❌ | reveal.js theme name (default: `white`) |
| `slides` | `list[SlideRecord]` | ✅ | Ordered slide definitions |
| `transition` | `str` | ❌ | Default transition for all slides (default: `slide`) |

## Relationships

- **DeckData** has many **SlideRecord** elements (ordered).
- **SlideRecord** entities sharing the same `id` form a **group** (typically a pair for auto-animate).
- Groups are unordered — the resolver processes all slides, groups by `id`, then assigns group-level attributes.
- One **DeckData** → one rendered `index.html`.

## Validation Rules

1. Layout enum must be a known value (Pydantic `Literal` ensures this at parse time).
2. At least one content field per slide (`title`, `body`, `code`), enforced by `model_validator`.
3. Auto-animate groups must have exactly 2 slides (steps 1 and 2). Groups of size 1 get no auto-animate; groups of size 3+ get sequential element_ids for each step.
4. Fragment indices: the resolver assigns sequential 1-based integers across the entire deck. Input `fragment_order` is IGNORED by the resolver — it is a rendering hint within a single slide only.
5. `raw` layout bypasses content transformation — body is inserted verbatim inside a bare `<section>`. The resolver still assigns `fragment_index` and `data_id` for structural consistency, but no auto-animate attributes or `element_ids`.

## Input/Output Schema

**Input** (LLM writes this):
```json
{
  "title": "Present Perfect",
  "theme": "white",
  "slides": [
    {
      "layout": "content",
      "id": "lead-in",
      "step": 1,
      "title": "Have you ever...?",
      "body": "eaten something strange?",
      "notes": "Elicit answers. Point to picture."
    },
    {
      "layout": "auto-animate-pair",
      "id": "tense-formation",
      "step": 1,
      "title": "Present Perfect",
      "body": "Subject + **have/has** + past participle"
    },
    {
      "layout": "auto-animate-pair",
      "id": "tense-formation",
      "step": 2,
      "title": "Present Perfect",
      "body": "She ***has visited*** Japan.\nThey ***have finished*** their homework."
    }
  ]
}
```

**Output** (resolver produces, macros consume):
```json
{
  "title": "Present Perfect",
  "theme": "white",
  "slides": [
    {
      "layout": "content",
      "id": "lead-in",
      "step": 1,
      "title": "Have you ever...?",
      "body": "eaten something strange?",
      "notes": "Elicit answers...",
      "data_id": "slide-lead-in-1",
      "element_ids": {"title": "el-lead-in-title", "body": "el-lead-in-body"},
      "auto_animate": false,
      "auto_animate_group_id": null,
      "fragment_index": 1
    },
    {
      "layout": "auto-animate-pair",
      "id": "tense-formation",
      "step": 1,
      "title": "Present Perfect",
      "body": "Subject + have/has + past participle",
      "data_id": "slide-tense-formation-1",
      "element_ids": {"title": "el-tense-formation-title", "body": "el-tense-formation-body"},
      "auto_animate": true,
      "auto_animate_group_id": "group-tense-formation",
      "fragment_index": 2
    },
    {
      "layout": "auto-animate-pair",
      "id": "tense-formation",
      "step": 2,
      "body": "She ***has visited*** Japan.\nThey ***have finished*** their homework.",
      "data_id": "slide-tense-formation-2",
      "element_ids": {"title": "el-tense-formation-title", "body": "el-tense-formation-body"},
      "auto_animate": true,
      "auto_animate_group_id": "group-tense-formation",
      "fragment_index": 3
    }
  ]
}
```
