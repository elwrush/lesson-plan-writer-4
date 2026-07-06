# Renderer Contract

## `render.py` CLI Interface

```
python render.py --template TEMPLATE_NAME --data DATA_FILE [options]
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `--template` | ✅ | Template name (without extension). Loads `templates/{name}.html` |
| `--data` | ✅ | Path to JSON data file, or `-` for stdin |
| `--output` / `-o` | ✅ | Output `.pdf` file path |
| `--css` | ❌ | Path to additional CSS file. Injected after the template's default CSS |
| `--no-ghostscript` | ❌ | Skip the Ghostscript pdfwrite normalisation step. Output is the raw WeasyPrint PDF |

### Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success — PDF(s) written |
| 1 | Invalid arguments (missing --template, --data, --output) |
| 2 | Validation error (Pydantic rejected input data) |
| 3 | Render error (Jinja2 template error, WeasyPrint failure) |
| 4 | File error (template not found, data file not found, output path unwritable) |
| 5 | Ghostscript error (`gs` failed during normalisation) |

### `render.py` Function Signatures

```
resolve_skill_root() -> Path
    Returns the absolute path to the skill directory (~/.kilo/skills/jinja-weasy-docs/)
    by resolving from __file__ location.

load_template(name: str) -> jinja2.Template
    Loads a Jinja2 template from templates/{name}.html.
    Uses FileSystemLoader with the templates/ directory as search path.
    Raises FileNotFoundError if template does not exist.

load_css(name: str) -> str
    Reads {name}.css from templates/ directory. Returns content as string.
    Raises FileNotFoundError if CSS file does not exist.

embed_image_as_data_uri(path: Path) -> str
    Reads a PNG file, returns a base64 data URI string.
    Format: data:image/png;base64,<encoded>

validate_envelope(data: dict) -> InputEnvelope
    Validates input dict against the InputEnvelope Pydantic model.
    Envelope contains: {"shape": {...shape data...}, "metadata": {...metadata...}}.
    Raises pydantic.ValidationError on failure.

merge_envelope_into_lesson(envelope: InputEnvelope) -> LessonPlanData
    Extracts stages from envelope.shape.example_lesson_plan.stages,
    converts shape field names (stage_aim → goal, time → time_minutes)
    to StageData, and merges with envelope.metadata fields.
    Returns a LessonPlanData ready for template rendering.

build_render_context(lesson: LessonPlanData, css_paths: list[Path]) -> dict
    Assembles the Jinja2 context: lesson data, logo data URIs, inline CSS.
    CSS files are read and concatenated into a single css_inline string.

render_html(template: jinja2.Template, context: dict) -> str
    Renders the Jinja2 template with the given context.
    Returns a complete HTML document as a string.
    Raises jinja2.TemplateError on render failure.

render_pdf(html_string: str, output_path: Path) -> None
    Converts the HTML string to PDF via WeasyPrint and writes to output_path.
    Uses weasyprint.HTML(string=html_string).write_pdf(target=output_path).
    Raises OSError on write failure.

normalise_pdf(input_path: Path, output_path: Path) -> bool
    Applies Ghostscript pdfwrite normalisation to the input PDF.
    Invokes: gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.7
        -dPDFSETTINGS=/printer -dEmbedAllFonts=true -dSubsetFonts=true
        -dDetectDuplicateImages=true -dOptimize=true
        -dNOPAUSE -dQUIET -dBATCH
        -sColorConversionStrategy=LeaveColorUnchanged
        -sOutputFile={output_path} {input_path}
    If gs is not on PATH, emits warning and copies input_path to output_path.
    Returns True if normalisation was applied, False if skipped (gs missing).
    Raises subprocess.CalledProcessError on Ghostscript failure.
```

### Contract Tests

1. CLI with `--template missing` → exit code 4, stderr contains "Template not found"
2. CLI with `--data invalid.json` (malformed JSON) → exit code 2, stderr contains Pydantic validation error
3. CLI with `--template base --data '{"title":"test"}' -o /tmp/test.pdf` → exit code 0, file created at /tmp/test.pdf
4. CLI with `--no-ghostscript` → PDF produced but `gs` not invoked (verified by mocking or inspecting temp file)
5. Ghostscript normalisation → `pdffonts` on output shows all fonts embedded (ArialMT, Arial-BoldMT)
6. Ghostscript not installed → warning to stderr, output file is raw WeasyPrint PDF (still valid)
