# Research: Lesson Plan Writer Pipeline

## Library Compatibility

| Dependency | Version | Compatible | Notes |
|---|---|---|---|
| Python | 3.12+ | ✅ | System python3 on Ubuntu 22.04+ / WSL |
| jinja2 | 3.1.x | ✅ | Mature, well-documented, no breaking changes expected |
| weasyprint | 62+ | ✅ | Actively maintained (releases every 2-3 months). Requires system libs: libpango-1.0-0, libcairo2, libffi8 |
| pydantic | 2.x | ✅ | `model_validate()` and `field_validator` confirmed working |
| Arial | system | ✅ | Available on all platforms (Windows, macOS, Linux via `ttf-mscorefonts-installer` or `fonts-freefont-ttc` fallback) |

## WeasyPrint Capabilities

### Confirmed Working (CSS Paged Media)
- `@page` rules with margin boxes (`@top-left`, `@top-center`, `@top-right`) — **supported**
- `page-break-before`, `page-break-after`, `page-break-inside` — **supported** (also `break-before`/`break-after`/`break-inside` CSS3 aliases)
- `orphans` / `widows` for paragraph-level pagination — **supported**
- `string-set` + `content: string()` for running headers — **supported**
- `counter(page)` / `counter(pages)` — **supported** (single-pass, no two-pass needed)
- Named pages (`@page stages { ... }`) — **supported**
- `@page:first`, `@page:blank`, `@page:left`, `@page:right` selectors — **supported**
- Flexbox — **solid** in WeasyPrint 62+
- CSS Grid — **mostly supported** (basic grids work; subgrid and complex `grid-template-areas` are partial)
- `element()` function for running elements — **supported** (use `position: running(NAME)` and `content: element(NAME)`)

### Current Limitations (WeasyPrint 62+)
- CSS Grid: subgrid not supported. Complex nested grids may need flexbox fallback
- `footnote` display type: not supported (not needed for lesson plans, but worth noting for future)
- PDF/A generation: not natively supported (would need post-processing)
- Image rendering: PNG and JPEG supported; SVG partially supported (no external resource resolution)

### Alternative: pdfkit (wkhtmltopdf wrapper)
- **Pros**: WebKit rendering engine, excellent CSS support including Grid
- **Cons**: Deprecated wkhtmltopdf, no active development, security issues with older Qt/WebKit
- **Verdict**: Rejected. WeasyPrint is actively maintained; wkhtmltopdf is not

### Alternative: Playwright (headless Chromium → PDF)
- **Pros**: Full Chromium rendering, absolute best CSS support
- **Cons**: ~300MB Chromium download, heavy dependency, slow startup, overkill for document generation
- **Verdict**: Rejected. WeasyPrint's CSS Paged Media support is sufficient for this use case

## CSS Paged Media Patterns for Lesson Plans

### Masthead header band

The masthead appears only on page 1 (header area), not as a running header on subsequent pages. Two approaches:

**Approach 1 (Recommended)**: Render masthead as normal content at the top of the HTML body. Use `@page:first` margin boxes only for page number or continuation markers. This avoids `element()` complexity and keeps the masthead in the normal flow.

**Approach 2**: Use `position: running(masthead)` on the masthead block, then `@page:first { @top-left { content: element(masthead) } }`. More complex but allows the masthead to live in the page margin box. Not needed here since the masthead only appears on page 1 content area.

### Stage table pagination

The stages table needs careful break control:

```css
.stage-section {
    break-inside: avoid-page;  /* Keep each stage together if possible */
}
.stage-header {
    break-after: avoid;  /* Keep stage name with its first data row */
}
.stages-table {
    break-inside: auto;  /* Allow the table itself to break across pages */
}
```

This ensures:
- Short stages don't split across pages
- Stage headers stay with their first row
- Long stages with many procedure items can break across pages

### Column widths in the stages table

From the reference PDF analysis:
- Time column: narrow (~1.5cm) — `width: 8%`
- Goal column: medium (~4cm) — `width: 22%`
- Procedure column: main column (~9cm) — `width: 55%`
- Int column: narrow (~1.5cm) — `width: 8%`

WeasyPrint respects `table-layout: fixed` with explicit column widths.

## Logo handling

Two options for embedding logos in the HTML:

**Option A (Recommended)**: Convert PNGs to data URIs at render time and inject into the Jinja2 context as `logo_left_data_uri` and `logo_right_data_uri`. This produces a fully self-contained HTML file.

```python
import base64
with open("assets/cambridge.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
    data_uri = f"data:image/png;base64,{b64}"
```

**Option B (Not recommended for portability)**: Reference files via relative paths from the skill directory. Paths break when the HTML is rendered from a different working directory.

## Font availability

Arial is the target font. On Linux:
- **Ubuntu/Debian**: `sudo apt install ttf-mscorefonts-installer` provides Arial
- **Fallback**: `fonts-freefont-ttc` provides FreeSans (metric-compatible with Arial)
- **WSL**: Windows fonts are accessible via `/mnt/c/Windows/Fonts/arial.ttf`

WeasyPrint uses system fontconfig. The CSS `font-family: Arial, Helvetica, sans-serif` will fall back gracefully.

## Ghostscript as concluding normalisation step

### Why Ghostscript

Adobe Acrobat's "flattening" process (triggered by print-to-PDF, "Save as Optimized PDF", or PDF/A conversion) re-interprets the PDF's internal structure. WeasyPrint produces valid PDF, but its internal representation (transparency groups, form XObjects, font subsetting metadata) can cause Acrobat to misinterpret element positions — shifting text or images. This is not a WeasyPrint bug; it is a consequence of different PDF engines using different internal representations.

Ghostscript's `pdfwrite` device completely rewrites the PDF from scratch using canonical PDF drawing operations. The output contains no non-standard structures, no ambiguous metadata — just standard PDF operators that every consumer (Acrobat, Preview, printer firmware) interprets identically. Some organisations run 100% of their PDFs through Ghostscript before their print workflow specifically to eliminate these issues.

### Recommended command

```bash
gs -sDEVICE=pdfwrite \
   -dCompatibilityLevel=1.7 \
   -dPDFSETTINGS=/printer \
   -dEmbedAllFonts=true \
   -dSubsetFonts=true \
   -dDetectDuplicateImages=true \
   -dOptimize=true \
   -dNOPAUSE -dQUIET -dBATCH \
   -sColorConversionStrategy=LeaveColorUnchanged \
   -sOutputFile=output.pdf \
   input.pdf
```

### Flag rationale

| Flag | Effect |
|---|---|
| `-dCompatibilityLevel=1.7` | Produces PDF 1.7 (ISO 32000-1). Modern enough for all current PDF viewers and printers, old enough for maximum compatibility |
| `-dPDFSETTINGS=/printer` | High-quality preset: 300dpi image resolution, font embedding on, colour images downsampled with bicubic interpolation. Use `/prepress` for archival quality (no downsampling, embedded ICC profiles) |
| `-dEmbedAllFonts=true` | Forces every referenced font to be embedded in the output. Eliminates font substitution at print time — the single most common cause of text reflow |
| `-dSubsetFonts=true` | Embeds only the glyphs actually used (not the entire font file). Reduces file size without affecting render correctness |
| `-dDetectDuplicateImages=true` | Identifies identical images (by MD5 hash) and embeds only one copy. The logo is referenced by both pages but stored once |
| `-dOptimize=true` | Linearizes the PDF for fast web view — useful if PDFs are served from a browser before printing |
| `-sColorConversionStrategy=LeaveColorUnchanged` | Passes WeasyPrint's colour space through unmodified. Prevents unexpected colour shifts that `UseDeviceIndependentColor` or `RGB` strategies can introduce |
| `-dNOPAUSE -dQUIET -dBATCH` | Batch mode — no prompts, no progress output, exits after completion |

### What NOT to use

| Flag | Why to avoid |
|---|---|
| `-dNOTRANSPARENCY` | Forces Ghostscript to rasterize any page containing transparency to a bitmap. WeasyPrint may use CSS opacity or RGBA colours that create transparency groups — this would flatten them to a pixel image, destroying vector quality |
| `-dUseCIEColor` | Applies CIE-based colour conversion that can shift colour appearance. Not needed for lesson plans which are monochrome/grayscale |
| `-dNoOutputFonts` | Converts all text to vector outlines. Produces huge files and prevents text selection/search |
| `-sColorConversionStrategy=RGB` or `=CMYK` | Unnecessary conversion step. Leave WeasyPrint's colour space unchanged |

### Cost

Ghostscript adds ~1-2 seconds to the pipeline for a 2-page lesson plan (dependent on image complexity). Total single-document pipeline: ~3-4s.

### Graceful degradation

If `gs` is not on PATH, the pipeline emits a warning and copies the intermediate WeasyPrint PDF as the final output. The user can install Ghostscript later and re-run with the same intermediate PDF.

### Ghostscript version

Ghostscript 10.0+ recommended. All flags used are available since GS 9.x. On Ubuntu/WSL: `sudo apt install ghostscript`.

## Performance

- **Single lesson plan**: Jinja2 render <10ms + WeasyPrint ~2s + Ghostscript ~1.5s = ~3.5s total
- **Memory**: WeasyPrint ~50-100MB, Ghostscript ~30-50MB. Both run sequentially, so peak memory is ~100MB

## Security

- **No network access**: WeasyPrint runs entirely locally. No CDN, no API calls.
- **No arbitrary file reads**: `render.py` only reads files from the skill directory (templates, assets, CSS).
- **Data URIs are self-contained**: No external resource loading.
- **Jinja2 sandbox**: Not needed — templates are authored by developers, not users. `jinja2.Environment()` with default settings is sufficient.
- **Pydantic validation**: Catches malformed input before any rendering occurs.

## Version Guidance

- WeasyPrint 62: First stable release with reliable CSS Grid support. Ship with >= 62.
- Jinja2 3.1: `{% extends %}` and `{% block %}` are stable. No issues.
- Pydantic 2.x: `model_validate()` available since 2.0. Use `field_validator` decorator for constraint checks.
- Python 3.12: `pathlib.Path` improvements. No syntax features required that aren't in 3.10+.
