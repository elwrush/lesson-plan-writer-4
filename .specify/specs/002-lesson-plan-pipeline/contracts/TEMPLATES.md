# Jinja2 Template Contracts

## Template Resolution

- Templates are loaded from `templates/` directory relative to the skill root
- Template name is passed without extension: `--template lesson-plan` loads `templates/lesson-plan.html`
- Templates use Jinja2's `{% extends %}` mechanism — `lesson-plan.html` extends `base.html`
- Template blocks are the extension points. Any template in the skill directory can extend any other.

## `base.html`

The root template. All document templates extend this.

### Blocks

| Block | Description | Default Content |
|---|---|---|
| `head` | Content inside `<head>`. Contains CSS injection and meta tags. | Renders `css_inline` in `<style>`, sets charset and viewport |
| `body_content` | Everything inside `<body>`. Wraps `pre_content`, `content`, `post_content`. | Renders `pre_content`, `content`, `post_content` in order |
| `pre_content` | Content before the main document content (e.g., masthead) | Empty |
| `content` | Main document body | Empty |
| `post_content` | Content after the main body (e.g., closing notes) | Empty |

### Context Variables Used

| Variable | Type | Source | Description |
|---|---|---|---|
| `css_inline` | `str` | render.py | Combined CSS from base.css and template CSS, injected via `<style>` |

### Page Geometry

```css
@page {
    size: A4;
    margin: 0.75in;
}
@page:first {
    margin-top: 1.25in;  /* Extra space for header band */
}
```

## `lesson-plan.html`

Extends `base.html`. Produces the full lesson plan layout.

### Blocks Overridden

| Block | Content |
|---|---|
| `pre_content` | Masthead: logo grid (Cambridge left, title center, ACT right) + horizontal rule |
| `content` | Metadata grid, Lesson Aim section, Stages table |

### Context Variables Used (in addition to base.html)

| Variable | Type | Description |
|---|---|---|
| `lesson` | `LessonPlanData` | The full validated lesson plan data |
| `logo_left_data_uri` | `str` | Cambridge logo as data URI |
| `logo_right_data_uri` | `str` | ACT logo as data URI |
| `template_css` | `str` | Lesson-plan-specific CSS (injected after base.css) |

### Template Structure (conceptual)

```
{% extends "base.html" %}

{% block pre_content %}
<div class="masthead">
    <div class="masthead-grid">
        <img src="{{ logo_left_data_uri }}" class="logo-left" alt="">
        <span class="masthead-title">C·E·L Mathayom</span>
        <img src="{{ logo_right_data_uri }}" class="logo-right" alt="">
    </div>
    <hr class="masthead-rule">
</div>
{% endblock %}

{% block content %}
<h1 class="doc-title">Lesson Plan</h1>
<h2 class="doc-subtitle">Topic: {{ lesson.topic }}</h2>

<div class="metadata-grid">
    <!-- Teacher / Date row -->
    <span class="label">Teacher:</span>
    <span class="value">{{ lesson.teacher }}</span>
    <span class="label">Date:</span>
    <span class="value">{{ lesson.date }}</span>
    <!-- ... more rows ... -->
</div>

<h2 class="section-title">Lesson Aim</h2>
<p class="aim"><strong>Main aim:</strong> {{ lesson.main_aim }}</p>
{% if lesson.subsidiary_aim %}
<p class="aim"><strong>Subsidiary aim:</strong> {{ lesson.subsidiary_aim }}</p>
{% endif %}

<h2 class="section-title">Lesson Stages</h2>
<table class="stages-table">
    <thead>
        <tr><th>Time</th><th>Goal</th><th>Procedure</th><th>Int</th></tr>
    </thead>
    <tbody>
    {% for stage in lesson.stages %}
        <tr class="stage-section">
            <td colspan="4" class="stage-header">STAGE {{ stage.stage_number }}: {{ stage.stage_name }}</td>
        </tr>
        <tr class="stage-row">
            <td class="time">{{ stage.time_minutes }} min</td>
            <td class="goal">{{ stage.goal }}</td>
            <td class="procedure">
                <ul>
                {% for step in stage.procedure %}
                    <li>{{ step }}</li>
                {% endfor %}
                </ul>
            </td>
            <td class="interaction">{{ stage.interaction }}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
{% endblock %}
```

### Contract Tests

1. Template renders without error given valid LessonPlanData
2. Masthead logos render as `<img>` tags with `src` containing data URIs
3. Metadata grid contains all required labels (Teacher, Date, Class, Duration, CEFR Level, Lesson Shape, Materials)
4. Stage header row spans all 4 columns via `colspan="4"`
5. Procedure items render as `<li>` elements inside `<ul>`
6. Empty `subsidiary_aim` omits the subsidiary aim paragraph
7. Empty `materials` omits the materials row (or renders it with no bullet)
8. Each stage renders as a `stage-section` block with `stage-header` merged row + `stage-row` data row
