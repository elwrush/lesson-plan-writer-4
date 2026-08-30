#!/usr/bin/env python3
"""Renders ONE combined Reciprocal Teaching booklet for BOTH levels (B1 then B2)
using the BOOK-REPORT-PRODUCTION report.html layout (adapted) + a New Yorker-style
pen-and-ink inset.

The two levels share Tasks 1, 2 and 5 verbatim (same structure, same roles,
same discussion questions). Only Task 3 (the chunk text) and Task 4 (the model
discussion) are differentiated, so they appear TWICE: the Level B1 version first,
then the Level B2 version. There is ONE header for the whole document.

Layout: Jinja2 template -> Playwright print-to-A4.
Logos are composited onto opaque white (decision-44 fix) so Chromium does not
embed a soft mask -> no Acrobat runtime transparency flattening.
"""
import argparse, tempfile
from pathlib import Path
from jinja2 import Template

PROJECT = Path("/mnt/c/PROJECTS/LESSON-PLAN-WRITER-4")
PROJ = PROJECT / "PROJECTS" / "READING LESSON FLUENCY"
TEMPLATE = PROJ / "SCRIPTS" / "rt_worksheet.html"
PDF_DIR = PROJ / "PDF"
ILLO = PROJ / "assets" / "rt-groups-reading.png"
LOGOS = {"masthead_left": PROJECT / "ASSETS" / "cambridge.png",
         "masthead_right": PROJECT / "ASSETS" / "ACT.png"}


def opaque_asset(path: Path) -> str:
    """Return a file:// URI pre-flattened to opaque RGB (no alpha soft mask)."""
    from PIL import Image
    im = Image.open(path)
    if "A" not in im.mode:
        return path.resolve().as_uri()
    rgb = Image.new("RGB", im.size, (255, 255, 255))
    rgb.paste(im, mask=im.getchannel("A"))
    tmp = Path(tempfile.gettempdir()) / f"{path.stem}_opaque_ws.png"
    rgb.save(tmp, format="PNG")
    return tmp.resolve().as_uri()


# ---- Content ----
CHUNK_HEADING = "What Is Going Wrong \u2014 the causes of the decline"

B1_CHUNK = (
    "The most obvious cause of the reading decline is the shift from print to screens. "
    "Over the past fifteen years, the amount of time that young people spend reading books "
    "has fallen sharply. At the same time, the time spent on smartphones, social media, and "
    "video platforms has risen dramatically. A 2025 systematic review (a study that combines "
    "many earlier studies) covering reading habits across two generations found that the "
    "decline began among millennials and has accelerated among Generation Z. The researchers "
    "identified several reasons. Short-form digital content trains the brain to skim rather "
    "than read deeply. Social media posts, TikTok videos, and WhatsApp messages all encourage "
    "fast, shallow reading. Notifications interrupt focus. And with so many things fighting "
    "for their attention, it is harder for young people to choose a book over a screen. "
    "Smartphones are a particular problem for reading. A 2024 study of EFL students "
    "identified ten distinct types of smartphone distraction during reading activities. "
    "These ranged from checking social media notifications to watching short videos. The "
    "researchers found that even the presence of a smartphone on a desk, switched off, reduced "
    "reading comprehension. The device does not need to be active to cause harm. Its mere "
    "existence creates a pull that weakens focus. Other studies in different countries and age "
    "groups have confirmed this finding."
)

B2_CHUNK = (
    "The most obvious cause of the reading decline is the shift from print to screens. Over "
    "the past fifteen years, the amount of time that young people spend reading books and "
    "long-form text has fallen sharply, while the time spent on smartphones, social media, and "
    "video platforms has risen dramatically. A 2025 systematic review (a study that combines "
    "many earlier studies) covering reading habits across two generations found that the "
    "decline began among millennials and has accelerated among Generation Z. The researchers "
    "identified several mechanisms. Short-form digital content trains the brain to skim rather "
    "than read deeply. Social media posts, TikTok videos, and WhatsApp messages all encourage "
    "fast, shallow reading. Notifications interrupt sustained attention. And the sheer volume "
    "of competing stimuli makes it harder for young people to choose a book over a screen. "
    "Smartphones are a particular problem for reading. A 2024 study of EFL students identified "
    "ten distinct types of smartphone distraction during reading activities, ranging from "
    "checking social media notifications to watching short videos. The researchers found that "
    "even the presence of a smartphone on a desk, switched off, reduced reading comprehension. "
    "The device does not need to be active to cause harm. Its mere existence creates a "
    "cognitive pull that weakens focus. This finding has been confirmed in multiple studies "
    "across different countries and age groups."
)


def timeline_html():
    def step(n, who, what):
        return f"<p><strong style='color:#1a3a5c'>{n}. {who}</strong> &mdash; {what}</p>"
    return (
        "<p>The four roles follow one round of reading:</p>"
        + step("1", "Predict", "the <strong>Predictor</strong> looks at the heading and predicts what the chunk will say. Only the Predictor speaks.")
        + step("2", "Read", "everyone reads the chunk <strong>silently</strong>.")
        + step("3", "Clarify &rarr; Question &rarr; Summarise", "the other three roles speak in turn, building on each other.")
        + "<p style='font-style:italic'>Then <strong>rotate roles</strong> and do the next chunk.</p>"
    )


def role_card(name, desc, starters):
    li = "".join(f"<p style='margin:0.1em 0 0 0'>&bull; {s}</p>" for s in starters)
    return (f"<div class='sub-head'>{name}</div>"
            f"<p style='margin:0.15em 0 0.25em 0'>{desc}</p>{li}")


def transcript(lines):
    body = "".join(
        f"<p style='margin:0.2em 0 0 0'><strong style='color:#1a3a5c'>{n}:</strong> {l}</p>"
        for n, l in lines
    )
    return body


READ_MARK = "<p style='text-align:center;font-style:italic;color:#555;margin:0.4em 0 0.2em 0'>&#9654; &nbsp; ( students read the chunk silently ) &nbsp; &#9664;</p>"

DISCUSSIONS = [
    ("Chunk 1 \u00b7 Reading at fifteen predicts your future",
     "The report says reading well at fifteen can predict your future success. <strong>Do you think your reading level now will decide what you do later? Why / why not?</strong>"),
    ("Chunk 2 \u00b7 Reading pays at school and at work",
     "Reading helps at university and even in jobs for people who do not go to university. <strong>Is reading useful in your future job? What kind of job do you want, and does it need reading?</strong>"),
    ("Chunk 3 \u00b7 Reading can be learned, not born",
     "The text says reading is not a gift \u2014 it is learned through practice. <strong>Do you agree that anyone can become a good reader with practice? What have you tried?</strong>"),
    ("Chunk 4 \u00b7 Thailand\u2019s fall is sharpest",
     "Thailand\u2019s PISA reading score has fallen for two decades, and more students cannot read well enough. <strong>Why do you think this is happening in Thailand? Who or what is responsible?</strong>"),
]
DISCUSSION_HTML = "".join(
    f"<p style='margin:0.3em 0 0 0'><strong style='color:#1a3a5c'>{t}</strong><br>{q}</p>"
    for t, q in DISCUSSIONS
)

FRAMEWORK_ROWS = [
    ("1. Opinion", "Say what you think.", "In my opinion\u2026 / I think\u2026"),
    ("2. Reason", "Give a reason for your opinion.", "because\u2026 / I think this because\u2026"),
    ("3. Example from text", "Support it with the text.", "The text says\u2026 / In the article, it says\u2026"),
    ("4. Disagree", "Another view, politely.", "I\u2019m not sure I agree\u2026 / I see it differently\u2026"),
    ("5. Reason / Agree", "Give a reason, or agree and add a reason.", "I agree, and also\u2026 / That\u2019s a good point, because\u2026"),
    ("6. Negotiate to conclusion", "Agree together.", "So we agree that\u2026 / To sum up, we think\u2026"),
]
FRAMEWORK_HTML = (
    "<table class='framework'>"
    "<tr><th style='width:22%'>Step</th><th style='width:36%'>What to do</th><th>Example language</th></tr>"
    + "".join(f"<tr><td class='step'>{s}</td><td>{w}</td><td class='lang'>{l}</td></tr>"
              for s, w, l in FRAMEWORK_ROWS)
    + "</table>"
)

B1_BEFORE = [("Emma (Predictor)", "The heading is \u201cWhat Is Going Wrong \u2014 the causes of the decline\u201d. So I predict this chunk will talk about why people read less. Maybe phones?")]
B1_AFTER = [
    ("Jack (Clarifier)", "I didn\u2019t understand \u201csystematic review\u201d. The gloss says it is a study of many studies. So it\u2019s a big study with many people."),
    ("Sophie (Questioner)", "If it\u2019s such a big study, I wonder\u2026 why does it matter for students? Is it only about young people? I\u2019m a student too."),
    ("Jack (Clarifier)", "The text says a phone can make a \u201cpull\u201d even when it is off. So it\u2019s not about the phone being on \u2014 just having it near you."),
    ("Sophie (Questioner)", "That makes me wonder\u2026 can the same happen with a laptop, or only a phone?"),
    ("Liam (Summariser)", "The main point of this chunk is that screens and phones are the main reason young people read less, and even a phone in the room weakens focus."),
    ("Emma (Predictor)", "My prediction was right \u2014 it was about phones. Good summary, Liam."),
]
B2_BEFORE = [("Oliver (Predictor)", "The heading \u201cWhat Is Going Wrong \u2014 the causes of the decline\u201d tells me this chunk will explain why reading is falling, before any solutions. I predict the causes will be technological.")]
B2_AFTER = [
    ("Ava (Clarifier)", "I need to clarify \u201csystematic review\u201d and \u201cmechanisms\u201d. A review combines many earlier studies, and the \u201cmechanisms\u201d here are the reasons behind the decline."),
    ("Noah (Questioner)", "The text says a switched-off phone still reduces comprehension, and calls it a \u201ccognitive pull\u201d. I wonder\u2026 is it really the device, or just the habit of having it there?"),
    ("Ava (Clarifier)", "The text says the pull happens even when it\u2019s off, so it\u2019s not the screen itself \u2014 it\u2019s your attention being drawn to it."),
    ("Noah (Questioner)", "That makes me wonder\u2026 would the same happen with any device, or only a phone? And is it the same for digital reading as for paper?"),
    ("Mia (Summariser)", "The core argument is that the shift from print to screens, combined with persistent smartphone distraction, trains students to skim rather than read deeply. The strongest evidence is the \u201ccognitive pull\u201d \u2014 the device alone weakens focus."),
    ("Oliver (Predictor)", "My prediction held \u2014 the causes were technological. Excellent summary, Mia."),
]

# The four role cards + inset are SHARED verbatim across both levels.
ROLE_CARDS = [
    {"type": "task", "num": "2", "title": "The four roles",
     "body": "<p>Each person takes <strong>one role</strong>, then follows the steps above. One role happens <strong>before</strong> reading; the other three <strong>after</strong>.</p>"},
    {"type": "task_sub", "heading": "Before reading",
     "body": role_card("PREDICTOR", "Look at the heading and guess what the section will say.",
                       ["\u201cThe heading says\u2026 so I think this section will\u2026\u201d",
                        "\u201cI predict\u2026 because\u2026\u201d"])},
    {"type": "task_sub", "heading": "After reading",
     "body": role_card("CLARIFIER", "Say what was confusing and fix it with your group.",
                       ["\u201cI didn\u2019t understand when it said\u2026\u201d",
                        "\u201cThis is confusing because\u2026\u201d"])
              + role_card("QUESTIONER", "Ask a genuine \u2018I wonder\u2026\u2019 question, not a quick check.",
                          ["\u201cI wonder\u2026 why\u2026\u201d",
                           "\u201cWhat is the most important question this section answers?\u201d"])
              + role_card("SUMMARISER", "Say the main idea of the chunk in one sentence.",
                          ["\u201cThe main point of this section is\u2026\u201d",
                           "\u201cIn one sentence, this section tells us\u2026\u201d"])},
    {"type": "clear"},
]


def differentiated_task3(level, chunk):
    """Task 3 — Read and Learn, one per level."""
    return {"type": "task", "num": "3", "title": "Read and Learn",
            "body": f"<div class='chunk-head'><span class='title'>{CHUNK_HEADING}</span><span class='level'>{level}</span></div>{chunk}"}


def differentiated_task4(level, before, after):
    """Task 4 — Model discussion, one per level."""
    return {"type": "task", "num": "4", "title": "Model discussion",
            "body": f"<div class='sub-head'>&#9632; Before reading &nbsp;({level})</div>{transcript(before)}"
                    + READ_MARK
                    + f"<div class='sub-head'>&#9632; After reading &nbsp;({level})</div>{transcript(after)}"}


def build_blocks():
    """Assemble the SINGLE joined block list: shared 1/2/5 once, then B1 and B2 differentiated 3/4."""
    blocks = []
    # Task 1 — shared
    blocks.append({"type": "task", "num": "1", "title": "How one round works", "body": timeline_html()})
    # Inset illustration — shared, once
    blocks.append({"type": "inset", "src": ILLO.resolve().as_uri(),
                   "alt": "Four students discussing a book", "caption": "A group of four, one role each."})
    # Task 2 — shared
    blocks.extend(ROLE_CARDS)

    # Task 3 + Task 4 — LEVEL B1
    blocks.append({"type": "level_section", "level": "Level B1",
                   "sub": "Read the chunk, then follow the model discussion."})
    blocks.append(differentiated_task3("B1", B1_CHUNK))
    blocks.append(differentiated_task4("B1", B1_BEFORE, B1_AFTER))

    # Task 3 + Task 4 — LEVEL B2 (differentiated examples only)
    blocks.append({"type": "level_section", "level": "Level B2",
                   "sub": "The same chunk for the higher level. Read it, then read the model."})
    blocks.append(differentiated_task3("B2", B2_CHUNK))
    blocks.append(differentiated_task4("B2", B2_BEFORE, B2_AFTER))

    # Task 5 — shared, once
    blocks.append({"type": "task", "num": "5", "title": "Discuss with your group",
                   "body": "<p>Choose one question for each chunk you read. In your group of four, use the discussion framework below to structure your talk.</p>"
                           + f"<div class='sub-head'>Discussion questions</div>{DISCUSSION_HTML}"
                           + f"<div class='sub-head' style='margin-top:0.9em'>How to organise your discussion</div>{FRAMEWORK_HTML}"})
    return blocks


def render_booklet(out_path, level_label="B1 &middot; B2"):
    blocks = build_blocks()
    html = Template(TEMPLATE.read_text(encoding="utf-8")).render(
        title="Reciprocal Learning and Discussion",
        subtitle="",
        level=level_label,
        blocks=blocks,
        masthead_left=opaque_asset(LOGOS["masthead_left"]),
        masthead_right=opaque_asset(LOGOS["masthead_right"]),
    )
    # resolve relative asset srcs to opaque file:// URIs
    html = html.replace('assets/images/cambridge.png', opaque_asset(LOGOS["masthead_left"]))
    html = html.replace('assets/images/ACT.png', opaque_asset(LOGOS["masthead_right"]))

    out_path = PDF_DIR / out_path
    tmp_html = out_path.with_suffix(".html")
    tmp_html.write_text(html, encoding="utf-8")
    print(f"  [html] {tmp_html.name}")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(tmp_html.resolve().as_uri(), wait_until="networkidle")
        page.pdf(path=str(out_path), format="A4", print_background=True)
        browser.close()
    tmp_html.unlink(missing_ok=True)
    print(f"  [pdf]  {out_path.name}")
    return out_path


def main():
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    print("Rendering combined Reciprocal Teaching booklet (B1 + B2)...")
    render_booklet("reading-reciprocal-teaching-B1-B2.pdf")
    print("Done.")


if __name__ == "__main__":
    main()
