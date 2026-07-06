# Research: Layout-Driven Slides

## Library Compatibility

| Dependency | Version | Compatible | Notes |
|---|---|---|---|
| Python | 3.12+ (uv-managed) | ✅ | stdlib-only for slideshow_lib |
| jinja2 | 3.1.x | ✅ | Already in use; no breaking changes |
| pydantic | 2.x | ✅ | Already in use; `model_validate()` and `Literal` types confirmed |
| reveal.js | 6.0.1 | ✅ | CDN from jsDelivr — no local dependency |
| slideshow_lib | current | ✅ | 23 globals + 2 filters, 100 tests — read-only dependency |
| ruff | 0.15.20 | ✅ | LSP configured, no issues |
| jinja-lsp | latest | ⚠️ | Installed via `uv tool install jinja-lsp`. LSP config in `kilo.jsonc` verified for `.jinja2` extensions. No known compatibility issues with Jinja2 3.1.x. |

## Markdown Processing

Content slots (title, body, notes) are markdown. Jinja2 has no built-in markdown filter.

**Decision**: Add a `markdown_to_html` filter to `slideshow_lib` using the Python `markdown` library (`import markdown`) with the `extra` extension. This preserves slideshow_lib's "stdlib + jinja2" constraint except for the one `markdown` import.

**Why `markdown` library**: Well-tested, widely deployed, supports `extra` extension (tables, fenced code blocks, footnotes) which covers ELL lesson content formatting. Alternative (`mistune`) is smaller but less widely adopted.

**Dependency**: `python-markdown` — available via `uv add markdown` or `pip install markdown`. Small footprint (~50KB installed).

## Performance Considerations

- **Resolver**: O(n) where n = number of slides. Single pass to assign group ids + sequential fragment indices. No nested loops. Expected runtime <1ms for typical 15–30 slide decks.
- **Jinja2 macro dispatch**: O(1) per slide — simple `if/elif` chain on layout field. No performance concern.
- **CDN loading**: The rendered HTML loads reveal.js from jsDelivr CDN at page load. No change from current behavior.

## Security Implications

- **Raw layout escape hatch**: Content is inserted verbatim. This is by design — the raw layout is an explicit opt-in. Standard slides use macros only, which sanitize through Jinja2's autoescaping (when enabled).
- **No new network dependencies**: All data flows through existing paths (JSON → Pydantic → Jinja2 → HTML). No new files read from disk.

## Version Guidance

- `pydantic.Literal` for layout enum: available since Pydantic v2.0. Confirmed in use.
- `pydantic.model_validator(mode="after")` for cross-field validation: confirmed working.
- reveal.js `data-auto-animate-id` attribute: introduced in reveal.js 4.3+. Version 6.0.1 on CDN supports it fully.
- `jinja-lsp` currently at v0.2.x — basic syntax validation, not template-aware for macros. Sufficient for catching unclosed blocks and reference errors during development.
