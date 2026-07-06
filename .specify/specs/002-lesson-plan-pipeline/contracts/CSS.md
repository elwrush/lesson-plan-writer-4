# CSS Contract

## File Structure

| File | Purpose |
|---|---|
| `templates/base.css` | Shared styles: `@page` rules, typography, reset, utility classes |
| `templates/lesson-plan.css` | Lesson-plan-specific styles: masthead, metadata grid, stages table |

CSS is loaded at render time and inlined into `<style>` tags in the HTML `<head>`. This produces fully self-contained HTML files with no external CSS dependencies.

## `base.css` Contract

### `@page` Rules

```css
@page {
    size: A4;
    margin: 0.75in;
    @bottom-center {
        content: counter(page);
        font-family: Arial, sans-serif;
        font-size: 9pt;
    }
}
@page:first {
    @bottom-center {
        content: counter(page);
    }
}
@page :blank {
    @bottom-center { content: none; }
}
```

### Base Typography

```css
body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10pt;
    line-height: 1.4;
    color: #000;
}
h1 { font-size: 14pt; font-weight: bold; }
h2 { font-size: 12pt; font-weight: bold; }
```

### Utility Classes

```css
.page-break { break-before: page; }
.page-break-after { break-after: page; }
.avoid-break { break-inside: avoid; }
```

### Contract Tests

1. `@page` sets `size: A4` — verified by `pdfinfo` on output
2. Page counter appears at `@bottom-center` — verified by text extraction on multi-page output
3. `:blank` pages have no page number — verified by rendering a document that starts on an even page (forces blank verso)
4. `.page-break` class forces a page break before the element — verified by page count
5. Default font is Arial — verified by `pdffonts` on output (shows Arial embedded)

## `lesson-plan.css` Contract

### Masthead

```css
.masthead-grid {
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    margin-bottom: 6pt;
}
.logo-left { height: 1.2cm; }
.logo-right { height: 1.6cm; }
.masthead-title {
    text-align: center;
    font-size: 16pt;
    font-weight: bold;
}
.masthead-rule {
    border: none;
    border-top: 0.5pt solid black;
    margin: 0 0 12pt 0;
}
```

### Metadata Grid

```css
.metadata-grid {
    display: grid;
    grid-template-columns: auto 1fr auto 1fr;
    column-gap: 12pt;
    row-gap: 4pt;
    margin-bottom: 12pt;
}
.metadata-grid .label { font-weight: bold; }
.metadata-grid .materials { grid-column: 1 / -1; }
.metadata-grid .slideshow-url { grid-column: 1 / -1; }
```

### Stages Table

```css
.stages-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}
.stages-table th {
    font-weight: bold;
    text-align: left;
    border-bottom: 1pt solid black;
    padding: 4pt 6pt;
}
.stages-table th:nth-child(1) { width: 8%; }   /* Time */
.stages-table th:nth-child(2) { width: 22%; }  /* Goal */
.stages-table th:nth-child(3) { width: 58%; }  /* Procedure */
.stages-table th:nth-child(4) { width: 12%; }  /* Int */

.stage-section {
    break-inside: avoid;
}
.stage-header {
    font-weight: bold;
    padding: 6pt 6pt 2pt 6pt;
    border-bottom: none;
    break-after: avoid;
}
.stage-row td {
    padding: 2pt 6pt 6pt 6pt;
    vertical-align: top;
    border-bottom: 0.5pt solid #ccc;
}
.stage-row .time { white-space: nowrap; }
.stage-row .goal { }
.stage-row .procedure ul {
    list-style: none;
    padding-left: 0;
    margin: 0;
}
.stage-row .procedure li::before {
    content: "\2022";
    padding-right: 6pt;
}
.stage-row .procedure li {
    margin-bottom: 2pt;
}
.stage-row .interaction { white-space: nowrap; }
```

### Contract Tests

1. Masthead grid renders three items: left image, center text, right image — verified by presence in rendered HTML
2. Metadata grid has 4-column layout — verified by CSS grid computed style (or visual match to reference)
3. Stage table column widths match reference: Time ~8%, Goal ~22%, Procedure ~58%, Int ~12%
4. Stage header row spans all columns (`colspan="4"` in template) and is bold
5. Procedure items render as bulleted list with `•` prefix
6. `.stage-section` has `break-inside: avoid` — verified by pagination behavior
7. Logos render at correct heights (left 1.2cm, right 1.6cm)
