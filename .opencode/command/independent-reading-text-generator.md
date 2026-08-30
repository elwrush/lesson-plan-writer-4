---
description: Produce leveled independent-reading texts (A2-C1) for extended classroom reading. Asks for CEFR level, reading minutes, source text, then renders a print-ready A4 PDF with line numbers and gloss footers.
---

# Command: independent-reading-text-generator

## Usage

`/independent-reading-text-generator` — starts the interactive workflow to produce a leveled reading text.

## What it does

Generates an independent/extensive reading text for a specified CEFR level and time budget. Interactive: asks for level, minutes, source, then simplifies (A2/B1/B2), gates through Kimi review + human approval, and renders a print-ready A4 PDF with line numbers and gloss footers.

## Execution Flow

1. **Load the skill**: Use the `skill` tool to load `independent-reading-text-generator`. All workflow steps, algorithms, and rendering details are defined there.

2. **Follow the skill's Interactive Flow exactly** — do not skip steps, do not render before human approval.

3. **Output**: PDF goes to `INDEPENDENT-READING/PROJECTS/<PROJECT>/PDF/` per the skill's output spec.

## Constraints

- Never render before Gate 2 (human approval)
- Never skip the word-count verification (`[target, cap]`)
- Reuse existing scripts in `scripts/` — do not reimplement sanitise, word_count, gloss, kimi_gate, render, or verify
