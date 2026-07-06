# Data Model: Lesson Plan Writer Pipeline

## Entities

### LessonPlanData

The top-level input structure. Maps directly to the LESSON-SHAPES JSON schema extended with document-level metadata.

| Field | Type | Required | Description |
|---|---|---|---|
| `topic` | `str` | ✅ | Lesson topic display string (e.g., "Writing Emails – PET Exam Part 1") |
| `teacher` | `str` | ✅ | Teacher name |
| `date` | `str` | ✅ | Date string (e.g., "5 July, 2026") — stored as string to preserve formatting |
| `class_name` | `str` | ✅ | Class identifier (e.g., "M2/M3") |
| `duration_minutes` | `int` | ✅ | Lesson duration in minutes |
| `cefr_level` | `str` | ✅ | CEFR level (e.g., "B1") |
| `lesson_shape` | `str` | ✅ | Shape display name (e.g., "Productive Skills (Shape F - Productive Skills (Writing))") |
| `materials` | `list[str]` | ❌ | Array of material descriptions (including slideshow URL if applicable). Default: `[]` |
| `main_aim` | `str` | ✅ | Main lesson aim (full sentence) |
| `subsidiary_aim` | `str` | ❌ | Optional subsidiary aim |
| `stages` | `list[StageData]` | ✅ | Ordered lesson stages. At least 1 required. |

Validation rules:
- `stages` must have at least 1 element
- `duration_minutes` must be > 0 and <= 300
- `topic` must not be empty
- `teacher` must not be empty

### StageData

A single stage within a lesson plan.

| Field | Type | Required | Description |
|---|---|---|---|
| `stage_name` | `str` | ✅ | Stage title (e.g., "Lead-in"). Displayed as "STAGE N: {name}" |
| `stage_number` | `int` | ✅ | Sequential position. Must be 1-based, strictly increasing |
| `time_minutes` | `int` | ✅ | Duration for this stage in minutes |
| `goal` | `str` | ✅ | Brief goal description (one sentence with infinitive verb) |
| `procedure` | `list[str]` | ✅ | Ordered list of procedure steps (bullet items) |
| `interaction` | `str` | ✅ | Interaction pattern (e.g., "T-Ss", "Ss-Ss", "S", "T-Ss, S") |

Validation rules:
- `stage_number` must be >= 1 and sequential (no gaps, no duplicates within a lesson)
- `time_minutes` must be > 0. Parsed from shape `time` string via regex `(\d+)` — `"5 min"` → `5`. Parse failure → validation error
- `procedure` must have at least 1 item
- `stage_name` must not be empty

### RenderContext

Internal context passed to the Jinja2 template — not user-supplied.

| Field | Type | Source | Description |
|---|---|---|---|
| `lesson` | `LessonPlanData` | User input | Validated lesson data |
| `logo_left_data_uri` | `str` | Script-generated | Cambridge logo as data URI (base64 PNG) |
| `logo_right_data_uri` | `str` | Script-generated | ACT logo as data URI (base64 PNG) |
| `css_inline` | `str` | CSS file read | Combined CSS content, inlined in `<style>` |
| `template_css` | `str` | CSS file read | Template-specific CSS (injected after base.css) |

### MailMergeBatch

Used when processing multiple records.

| Field | Type | Required | Description |
|---|---|---|---|
| `records` | `list[LessonPlanData]` | ✅ | Array of lesson plans |
| `start_on_odd_page` | `bool` | ❌ | If true, each record starts on an odd-numbered page. Default: `false` |

## Relationships

- **LessonPlanData** has many **StageData** elements (ordered by `stage_number`).
- Stages form a strict sequence: `stage_number` starts at 1 and increments by 1.
- **LessonPlanData** → one rendered PDF document.
- Input envelope: `{"shape": {...shape content...}, "metadata": {teacher, date, class_name, ...}}`. The shape content provides stages and aims; metadata provides document-level fields.

## Validation Rules

1. `LessonPlanData.stages` must have >= 1 element. Zero-stage lessons are rejected.
2. `StageData.stage_number` must be 1-based sequential (1, 2, 3...). If input has gaps (1, 3, 4), validation error.
3. `StageData.time_minutes` must be > 0. Invalid stages rejected.
4. `StageData.procedure` must be a non-empty list. Empty procedure rejected.
5. `LessonPlanData.main_aim` must not be empty string. Source is `metadata.main_aim` (resolved text). `shape.main_aim_format` is a template pattern with placeholders and is NOT used as the rendered aim — metadata always wins.
6. Duration sum of all stages does NOT need to equal `duration_minutes` — they serve different purposes (stages are estimated, total is planned). No cross-field validation needed.
7. `date` is a free-form string — no date parsing attempted. Preserved as-is.

## Input/Output Schema

**Input** (user provides — envelope format):
```json
{
  "shape": {
    "name": "Productive Skills",
    "description": "Preparation → speaking/writing output.",
    "pedagogical_justification": "...",
    "main_aim_format": "...",
    "example_lesson_plan": {
      "header": "...",
      "stages": [
        {
          "stage": "Lead-in",
          "stage_number": 1,
          "stage_aim": "To activate learners' interest in the PET email task and set the context",
          "procedure": [
            "Show the splash and title slides. Elicit: \"What makes an email sound natural?\"",
            "Display the PET email task from Mrs Lake on the screen.",
            "Elicit what the four notes mean: Great!, Explain, Suggest ..., Tell Mrs Lake.",
            "Tell students: \"Today you will learn how to make your email flow naturally -- not just tick the boxes.\""
          ],
          "time": "5 min",
          "interaction": "T-Ss"
        }
      ]
    }
  },
  "metadata": {
    "teacher": "Ed Rush",
    "date": "5 July, 2026",
    "class_name": "M2/M3",
    "duration_minutes": 46,
    "cefr_level": "B1",
    "lesson_shape": "Productive Skills (Shape F - Productive Skills (Writing))",
    "topic": "Writing Emails – PET Exam Part 1",
    "materials": [
      "PET Writing Email worksheet",
      "Slideshow",
      "Slideshow URL: https://elwrush.github.io/lesson-plan-writer/M2-M3-WRITING-EMAIL/index.html"
    ],
    "main_aim": "By the end of the lesson, learners will have written a PET-style reply email using cohesive devices (As for, That way) to connect their ideas naturally.",
    "subsidiary_aim": "Learners will also have practised identifying key task requirements and evaluating model responses against cohesion criteria."
  }
}
```

**Internal** (RenderContext passed to Jinja2):
```json
{
  "lesson": { /* LessonPlanData as above */ },
  "logo_left_data_uri": "data:image/png;base64,iVBOR...",
  "logo_right_data_uri": "data:image/png;base64,iVBOR...",
  "css_inline": "@page { size: A4; ... }",
  "template_css": ".masthead { ... }"
}
```

**Output**: A4 PDF (595.276 × 841.89 pts), typically 2 pages for a standard lesson.
