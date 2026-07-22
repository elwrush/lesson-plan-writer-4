#!/usr/bin/env python3
"""Generate a B1-adapted Punctuation & Capitalisation worksheet for M2-4A."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

SKILL_ROOT = Path(os.environ.get("SKILL_ROOT", str(Path.home() / ".kilo" / "skills" / "write-test-worksheet")))
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from render import render_html_to_pdf

PROJECT_ROOT = Path(os.environ.get("LESSON_PLAN_WRITER_ROOT", "/mnt/c/PROJECTS/LESSON-PLAN-WRITER-4"))

dotenv_path = PROJECT_ROOT / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    load_dotenv()

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", str(PROJECT_ROOT / "PROJECTS" / "ANSWER SHEETS")))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PADDING_MAP = {1: 0, 2: 0, 3: 1, 4: 0, 5: 3}
PAGES_PER_STUDENT = 3
PADDING = PADDING_MAP.get(PAGES_PER_STUDENT, 0)
EXPECTED_TOTAL_PAGES = PAGES_PER_STUDENT + PADDING

LOGO_DIR = SKILL_ROOT / "assets"
LOGO_LEFT = LOGO_DIR / "cambridge.png"
LOGO_RIGHT = LOGO_DIR / "ACT.png"
LOGO_DATA_LEFT = LOGO_LEFT.resolve().as_uri() if LOGO_LEFT.exists() else ""
LOGO_DATA_RIGHT = LOGO_RIGHT.resolve().as_uri() if LOGO_RIGHT.exists() else ""

WORKSHEET_BODY = """
<h2>Task 1 &mdash; Recognise</h2>
<div class="instructions">
<strong>Instructions:</strong> Each sentence below contains errors in punctuation or capitalisation.
<strong>Circle</strong> each error and <strong>write</strong> the correction above it.
Sentences 1&ndash;2 have the errors <strong>boxed</strong> for you. For sentences 3&ndash;10,
find the errors yourself &mdash; the number of errors is shown in brackets.
</div>

<h3>Example</h3>
<div class="example-row">
  <span class="s-text">
    <span class="boxed">i</span> like to read books.
    &rarr;
    <span class="correction">I</span>
  </span>
</div>

<h3>Now try these:</h3>

<div class="task1-sentence">
  <div class="s-row"><span class="s-num">1.</span><span class="s-text">
    <span class="boxed">i</span> like to learn <span class="boxed">english</span>.
  </span></div>
  <div class="write-lines"><div class="wl"></div></div>
</div>

<div class="task1-sentence">
  <div class="s-row"><span class="s-num">2.</span><span class="s-text">
    My uncle works as a <span class="boxed">Manager</span>.
  </span></div>
  <div class="write-lines"><div class="wl"></div></div>
</div>

<div class="task1-sentence">
  <div class="s-row"><span class="s-num">3.</span><span class="s-text">
    She was born in Chiang Mai , Thailand.
    <span class="error-count">(1 error)</span>
  </span></div>
  <div class="write-lines"><div class="wl"></div></div>
</div>

<div class="task1-sentence">
  <div class="s-row"><span class="s-num">4.</span><span class="s-text">
    Even though it was raining We went outside.
    <span class="error-count">(2 errors)</span>
  </span></div>
  <div class="write-lines"><div class="wl"></div></div>
</div>

<div class="task1-sentence">
  <div class="s-row"><span class="s-num">5.</span><span class="s-text">
    My best friend who lives next door works as a Teacher.
    <span class="error-count">(3 errors)</span>
  </span></div>
  <div class="write-lines"><div class="wl"></div></div>
</div>

<div class="task1-sentence">
  <div class="s-row"><span class="s-num">6.</span><span class="s-text">
    In my opinion The school needs a new library.
    <span class="error-count">(2 errors)</span>
  </span></div>
  <div class="write-lines"><div class="wl"></div></div>
</div>

<div class="task1-sentence">
  <div class="s-row"><span class="s-num">7.</span><span class="s-text">
    My friend Anna likes to play football.
    <span class="error-count">(2 errors)</span>
  </span></div>
  <div class="write-lines"><div class="wl"></div></div>
</div>

<div class="task1-sentence">
  <div class="s-row"><span class="s-num">8.</span><span class="s-text">
    I was tired but I kept studying.
    <span class="error-count">(1 error)</span>
  </span></div>
  <div class="write-lines"><div class="wl"></div></div>
</div>

<div class="task1-sentence">
  <div class="s-row"><span class="s-num">9.</span><span class="s-text">
    I wanted to go to the party however I was sick.
    <span class="error-count">(2 errors)</span>
  </span></div>
  <div class="write-lines"><div class="wl"></div></div>
</div>

<div class="task1-sentence">
  <div class="s-row"><span class="s-num">10.</span><span class="s-text">
    Many Students like to play games at break time.
    <span class="error-count">(1 error)</span>
  </span></div>
  <div class="write-lines"><div class="wl"></div></div>
</div>

<h2>Task 2 &mdash; Recall</h2>
<div class="instructions">
<strong>Instructions:</strong> Each box below contains an error from Task 1. <strong>Explain the rule</strong> that was broken. Write a complete sentence explaining when and why this error occurs.
</div>

<div class="task2-item">
  <div><span class="boxed">Manager</span> / <span class="boxed">Teacher</span> (from sentences 2 &amp; 5)</div>
  <div><span style="font-weight:bold;">Common nouns like manager and teacher should not be capitalised. Only proper nouns need capitals.</span></div>
</div>

<div class="task2-item">
  <div><strong>1.</strong> <span class="boxed"> ,</span> (from sentence 3)</div>
  <div style="display:flex;align-items:baseline;"><span>Your rule:</span><span style="flex:1;border-bottom:1.5pt solid #222;height:1.3em;margin-left:0.3em;"></span></div>
</div>

<div class="task2-item">
  <div><strong>2.</strong> <span class="boxed">Anna</span> (from sentence 7)</div>
  <div style="display:flex;align-items:baseline;"><span>Your rule:</span><span style="flex:1;border-bottom:1.5pt solid #222;height:1.3em;margin-left:0.3em;"></span></div>
</div>

<div class="task2-item">
  <div><strong>3.</strong> <span class="boxed">We</span> / <span class="boxed">The</span> (from sentences 4 &amp; 6)</div>
  <div style="display:flex;align-items:baseline;"><span>Your rule:</span><span style="flex:1;border-bottom:1.5pt solid #222;height:1.3em;margin-left:0.3em;"></span></div>
</div>

<div class="task2-item">
  <div><strong>4.</strong> <span class="boxed">however</span> (from sentence 9)</div>
  <div style="display:flex;align-items:baseline;"><span>Your rule:</span><span style="flex:1;border-bottom:1.5pt solid #222;height:1.3em;margin-left:0.3em;"></span></div>
</div>

<div style="page-break-before:always;"></div>

<h2>Task 3 &mdash; Use</h2>
<div class="instructions">
<strong>Instructions:</strong> Write a paragraph of up to <strong>70 words</strong> describing a fun day you had with your family or friends. Focus on using correct punctuation and capitalisation.
</div>

<div class="writing-prompt">
<strong>Include all of the following in your paragraph:</strong>
<ul style="margin:0.3em 0 0 0;padding-left:1.2em;">
  <li>a sentence starting with <em>while</em> or <em>even though</em></li>
  <li>a sentence with extra information in commas (e.g., <em>my sister, Lisa, ...</em>)</li>
  <li>correct use of a comma before <em>and</em> or <em>but</em></li>
  <li>the word <strong>however</strong> used correctly to connect two ideas</li>
</ul>
</div>
"""

STYLES = """
@page { size: A4; margin: 1.6cm 1.8cm 1.8cm 1.8cm; }

body {
  font-family: Roboto, Arial, Helvetica, sans-serif;
  font-size: 14pt;
  line-height: 1.5;
  color: #222;
  margin: 0;
  padding: 0;
}

.masthead {
  display: grid;
  grid-template-columns: 0.8fr 1.4fr 0.8fr;
  align-items: center;
  margin-bottom: 0.1em;
}
.masthead-left { text-align: left; }
.masthead-left img { height: 1.6cm; }
.masthead-center { text-align: center; font-size: 16pt; font-weight: bold; letter-spacing: 0.5pt; }
.masthead-right { text-align: right; }
.masthead-right img { height: 1.0cm; }
.masthead-sep { border: none; border-top: 1.5pt solid #000; margin: 0 0 0.15em 0; }

.demographic {
  text-align: center;
  margin: 0.5cm 0 0.5cm 0;
  padding: 0.15em 0;
  border: 1pt solid #222;
  font-size: 14pt;
}
.demographic span { margin: 0 0.4em; }
.demographic .demo-bold { font-weight: bold; }

h1 {
  font-size: 20pt;
  text-align: center;
  margin: 0.1em 0 0em 0;
}
h2 {
  font-size: 14pt;
  margin: 0.4em 0 0.15em 0;
  padding: 0.1em 0.5em;
  background: #222;
  color: #fff;
}
h3 {
  font-size: 14pt;
  margin: 0.3em 0 0.1em 0;
  color: #222;
}

.cefr-tag {
  text-align: center;
  font-size: 14pt;
  color: #555;
  margin: 0 0 0.2em 0;
}

.instructions {
  font-size: 14pt;
  color: #444;
  margin: 0.15em 0 0.3em 0;
  padding: 0.3em 0.5em;
  background: #f0f0f0;
  border-left: 3pt solid #222;
}

.task1-sentence {
  page-break-inside: avoid;
  margin: 0.7em 0 0 0;
  text-align: left;
}
.task1-sentence .s-num {
  font-weight: bold;
  margin-right: 0.3em;
}
.task1-sentence .s-text {
  font-size: 14pt;
  line-height: 1.4;
}
.task1-sentence .error-count {
  font-size: 14pt;
  color: #444;
  font-style: italic;
  margin-left: 0.3em;
}
.task1-sentence .write-lines {
  margin: 0.2em 0 0 0;
}
.task1-sentence .write-lines .wl {
  border-bottom: 1pt solid #999;
  height: 1.5em;
}

.boxed {
  display: inline-block;
  border: 1.5pt solid #222;
  background: #e8e8e8;
  padding: 0.05em 0.2em;
  font-weight: bold;
  color: #222;
}

.example-row {
  margin: 0.3em 0 0 0;
}
.example-row .s-text { font-size: 14pt; }
.example-row .correction { font-weight: bold; color: #444; }

.task2-item {
  page-break-inside: avoid;
  margin: 0.3em 0 0 0;
  border-bottom: 1pt solid #ddd;
  padding-bottom: 0.2em;
}
.task2-item:last-child { border-bottom: none; }

.writing-prompt {
  font-size: 14pt;
  color: #444;
  margin: 0.3em 0 0.3em 0;
  padding: 0.3em 0.5em;
  background: #f0f0f0;
  border: 1pt solid #999;
}
"""


def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ESL_KEY")
    if not url:
        raise RuntimeError("SUPABASE_URL not set")
    if not key:
        raise RuntimeError("SUPABASE_ESL_KEY not set")
    return create_client(url, key)


def fetch_students(class_name: str, sb):
    resp = sb.table("classlists") \
        .select("student_id, name") \
        .eq("class", class_name) \
        .order("name") \
        .execute()
    return resp.data or []


def build_student_html(student, class_name, body, styles, logo_left, logo_right, padding_pages):
    padding_divs = ""
    for _ in range(padding_pages):
        padding_divs += '<div style="page-break-before:always;"></div>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>{styles}</style>
</head>
<body>

<div class="masthead">
  <div class="masthead-left">{'<img src="' + logo_left + '" alt="">' if logo_left else ''}</div>
  <div class="masthead-center">C·E·L Mathayom</div>
  <div class="masthead-right">{'<img src="' + logo_right + '" alt="">' if logo_right else ''}</div>
</div>
<hr class="masthead-sep">

<div class="demographic">
  <span>Name: <span class="demo-bold">{student['name']}</span></span>
  <span>ID: <span class="demo-bold">{student['student_id']}</span></span>
  <span>Class: <span class="demo-bold">{class_name}</span></span>
</div>

{body}

{padding_divs}
</body>
</html>"""


def count_pdf_pages(path: Path) -> int:
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            capture_output=True, text=True, timeout=15
        )
        for line in result.stdout.splitlines():
            if line.startswith("Pages"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate Punctuation & Capitalisation worksheet for M2-4A.")
    parser.add_argument("--class", dest="class_name", default="M2-4A", help="Class name")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sb = get_supabase()
    students = fetch_students(args.class_name, sb)
    if not students:
        print(f"No students found for {args.class_name}")
        sys.exit(1)

    print(f"{len(students)} students in {args.class_name}")
    output_pdf = output_dir / f"{args.class_name}-Punctuation-Capitalisation-B1.pdf"

    lint_errors = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        pdfs = []

        for s in students:
            html = build_student_html(
                student=s,
                class_name=args.class_name,
                body=WORKSHEET_BODY,
                styles=STYLES,
                logo_left=LOGO_DATA_LEFT,
                logo_right=LOGO_DATA_RIGHT,
                padding_pages=PADDING,
            )
            out = tmp / f"{s['student_id']}.pdf"
            render_html_to_pdf(html, out)
            pdfs.append(out)

            actual = count_pdf_pages(out)
            expected = EXPECTED_TOTAL_PAGES
            if actual != expected:
                lint_errors.append(
                    f"  FAIL {s['name']} ({s['student_id']}): "
                    f"expected {expected} pages, got {actual}"
                )
            else:
                print(f"  PASS {s['name']} ({s['student_id']}): {actual} pages")

        if lint_errors:
            print("\nLINT FAILURES:")
            for e in lint_errors:
                print(e)
            sys.exit(1)

        print(f"\nAll {len(pdfs)} student PDFs passed lint ({EXPECTED_TOTAL_PAGES} pages each).")

        if len(pdfs) == 1:
            pdfs[0].replace(output_pdf)
        else:
            gs_args = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
                       "-dPDFSETTINGS=/prepress",
                       f"-sOutputFile={output_pdf}", "-dCompatibilityLevel=1.7"]
            for p in pdfs:
                gs_args.append(str(p))
            subprocess.run(gs_args, check=True, timeout=120)

    pages = count_pdf_pages(output_pdf)
    print(f"\nWrote {output_pdf} ({pages} pages)")
    print(f"  {len(students)} students x {PAGES_PER_STUDENT} content pages + {PADDING} padding each (total {EXPECTED_TOTAL_PAGES}/student)")


if __name__ == "__main__":
    main()
