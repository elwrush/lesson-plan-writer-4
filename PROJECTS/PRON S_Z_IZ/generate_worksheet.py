#!/usr/bin/env python3
"""Generate the Plural-s Pronunciation Noticing worksheet (Shape L) for M2A/M3A.

Target feature: plural -s (/s/, /z/, /ɪz/) in the context of personal possessions.
Layout: project-local template (SCRIPTS/plural_s_worksheet.html) — the updated
C.R.A.P. format (navy accent #1a3a5c, boxed task headers, CEFR badge, floated
pen-and-ink inset, page numbers). Self-contained — no dependency on the legacy
write-test-worksheet worksheet.html template.
"""
import re
import subprocess
import tempfile
from pathlib import Path

from jinja2 import Template

POJECT_ROOT = Path("/mnt/c/PROJECTS/LESSON-PLAN-WRITER-4")
PROJ = POJECT_ROOT / "PROJECTS" / "PRON S_Z_IZ"
TEMPLATE = PROJ / "SCRIPTS" / "plural_s_worksheet.html"
PDF_DIR = PROJ
ILLO = PROJ / "assets" / "banner.jpg"
RENDER_PDF_JS = POJECT_ROOT / "scripts" / "render-pdf.js"
LOGOS = {
    "masthead_left": POJECT_ROOT / "ASSETS" / "cambridge.png",
    "masthead_right": POJECT_ROOT / "ASSETS" / "ACT.png",
}


def opaque_asset(path: Path) -> str:
    """Return a file:// URI pre-flattened to opaque RGB (no alpha soft mask)."""
    try:
        from PIL import Image
    except ImportError:
        return path.resolve().as_uri()
    im = Image.open(path)
    if "A" not in im.mode:
        return path.resolve().as_uri()
    rgb = Image.new("RGB", im.size, (255, 255, 255))
    rgb.paste(im, mask=im.getchannel("A"))
    tmp = Path(tempfile.gettempdir()) / f"{path.stem}_opaque_ws.png"
    rgb.save(tmp, format="PNG")
    return tmp.resolve().as_uri()


# ---------------------------------------------------------------------------
# Content helpers
# ---------------------------------------------------------------------------


def label_row(num: int, word: str) -> str:
    """One discrimination / tick-cross item with a label box."""
    return f"<p style='margin:0.25em 0 0 0'><strong>{num}.</strong> <span class='label-box'></span> {word}</p>"


def numbered_words(text: str, start: int = 0) -> str:
    """Wrap every plural target in a .target span with a [n] prefix."""
    counter = {"n": start}

    def repl(m: re.Match) -> str:
        counter["n"] += 1
        return f"[{counter['n']}] <span class='target'>{m.group(1)}</span>"

    # The word is wrapped in <strong>...</strong> by the caller; strip it here
    # so we can re-wrap as a .target span.
    return re.sub(r"<strong>(.*?)</strong>", repl, text)


FLORENCE_TRANSCRIPT = (
    "Um, my name is Kalaphat and my nickname is Florence and I'm, I'm, how old are you? "
    "I'm [0] <span class='target'>14 <strong>years</strong></span> old but next month I will be 15. "
    "Uh, I, I was born in Ayutthaya and come here to studies in Bangkok, so I now live in Bangkok "
    "near the, near the school, uh, like around 7-Eleven. I use it everyday like, uh, four "
    "<span class='target'><strong>hours</strong></span> [1] a day. "
    "And, yeah. Um, app and website I like best is, I think it's Instagram because their news feed "
    "is really interesting. It's related to the <span class='target'><strong>things</strong></span> [2] "
    "that I love and enjoy doing and also I can text with my "
    "<span class='target'><strong>friends</strong></span> [3] on it and also making a video call. "
    "Um, I see a girl writing a notebook and she has uh short hair and she wears a hoodie. "
    "Uh, she's writing, I think a homework and she's using her laptop to do her homework and on the "
    "desk it have a book, uh, three <span class='target'><strong>books</strong></span> [4]. "
    "Uh, they have science and English grammar and something I cannot read. On her background, uh, "
    "I can see her bed and her, on the wall it have <span class='target'><strong>pictures</strong></span> [5] "
    "hanging on it and she have a bookshelf that have many <span class='target'><strong>books</strong></span> [6] "
    "and a <span class='target'><strong>plants</strong></span> [7] on it. And also she's, uh, a table "
    "she's sitting is near a window and I think it's, uh, a day where, where she do it."
)

MODEL_READING = (
    "I love my <span class='target'><strong>things</strong></span> [1]. I have three "
    "<span class='target'><strong>books</strong></span> [2] on my desk, two "
    "<span class='target'><strong>dogs</strong></span> [3] in the garden, and four "
    "<span class='target'><strong>glasses</strong></span> [4] in the kitchen. My "
    "<span class='target'><strong>friends</strong></span> [5] come to my house and we play board "
    "<span class='target'><strong>games</strong></span> [6]. My "
    "<span class='target'><strong>siblings</strong></span> [7] have their own "
    "<span class='target'><strong>things</strong></span> [8] too. We have "
    "<span class='target'><strong>plants</strong></span> [9] in every room and "
    "<span class='target'><strong>pictures</strong></span> [10] on every wall. I like my house because it is full of "
    "<span class='target'><strong>things</strong></span> [11] that make me happy."
)


def build_blocks():
    blocks = []

    # ---- Part A ---- (magazine-style: text left, cartoon right, one grid row)
    blocks.append({
        "type": "fig_row",
        "num": "A",
        "title": "Listen. Can You Hear It?",
        "text": (
            "<p><strong>Instructions:</strong> Listen to the two recordings. One is Thai-style English. "
            "One is native English. In the native version, every word ends with its full sound. Tap your finger "
            "every time you hear a plural <strong>/s/</strong>, <strong>/z/</strong>, or <strong>/ɪz/</strong> at the end of a word.</p>"
            "<p style='margin-top:0.6em'><strong>Model sentence:</strong> I have three books, two dogs, and four glasses.</p>"
            "<p><strong>1.</strong> How many plural sounds did you hear? Write the number: <span class='label-box'></span></p>"
        ),
        "src": None,  # set in render via ILLO
        "alt": "Teacher at blackboard",
        "caption": "",
    })

    # ---- Part B ----
    blocks.append({
        "type": "task", "num": "B", "title": "Same or Different?",
        "body": (
            "<p><strong>Instructions:</strong> Listen to the recording. After each number you will hear a word "
            "<strong>twice</strong>. Are both pronounced the same, or is the plural sound missing the second time? "
            "Write <strong>&#10003;</strong> if both have the plural, or <strong>&#10007;</strong> if the plural is dropped.</p>"
            + label_row(1, "books") + label_row(2, "dogs") + label_row(3, "glasses")
            + label_row(4, "friends") + label_row(5, "years")
        ),
    })

    # ---- Part C ----
    blocks.append({
        "type": "task", "num": "C", "title": "Plural or Not?",
        "body": (
            "<p><strong>Instructions:</strong> Listen to the recording. After each number you will hear a word. "
            "Write <strong>&#10003;</strong> if you hear the plural ending, or <strong>&#10007;</strong> if it is missing.</p>"
            + label_row(1, "things") + label_row(2, "siblings") + label_row(3, "games")
            + label_row(4, "students") + label_row(5, "pictures") + label_row(6, "dinners")
            + label_row(7, "books") + label_row(8, "plants")
        ),
    })

    # ---- Part D ----
    blocks.append({
        "type": "task", "num": "D", "title": "The Plural Pattern",
        "body": (
            "<p><strong>Instructions:</strong> Say each word and clap the syllables. Write the number of syllables "
            "next to the word.</p>"
            "<p><strong>1.</strong> books &nbsp;&nbsp; ______ &nbsp; syllables</p>"
            "<p><strong>2.</strong> dogs &nbsp;&nbsp; ______ &nbsp; syllables</p>"
            "<p><strong>3.</strong> glasses &nbsp;&nbsp; ______ &nbsp; syllables</p>"
            "<p><strong>4.</strong> friends &nbsp;&nbsp; ______ &nbsp; syllables</p>"
            "<div class='rule-box'>"
            "<p class='rule-title'><strong>The rule</strong></p>"
            "<ul class='rule-list'>"
            "<li>After <strong>voiceless</strong> sounds (like /k/), -s sounds like <strong>/s/</strong>: "
            "<em>books</em> = 1 syllable.</li>"
            "<li>After <strong>voiced</strong> sounds (like /ɡ/), -s sounds like <strong>/z/</strong>: "
            "<em>dogs</em> = 1 syllable.</li>"
            "<li>After <strong>sibilants</strong> (like /s/, /z/, /ʃ/), -s sounds like <strong>/ɪz/</strong> "
            "and adds a syllable: <em>glasses</em> = 2.</li>"
            "</ul>"
            "<p class='rule-foot'><em>Drop the ending and the meaning is lost — <em>book</em> is one, "
            "<em>books</em> is many!</em></p>"
            "</div>"
        ),
    })

    # ---- Part E ----
    blocks.append({
        "type": "task", "num": "E", "title": "Does the Ending Matter?",
        "body": (
            "<p><strong>Instructions:</strong> Circle the correct form, then answer the question.</p>"
            "<p><strong>1.</strong> Circle the correct form: I have three (book / books).</p>"
            "<p><strong>2.</strong> Circle the correct form: She has two (dog / dogs).</p>"
            "<p><strong>3.</strong> Does <em>glasses</em> have more syllables than <em>glass</em>? "
            "<span class='label-box'></span> &nbsp; yes / no</p>"
        ),
    })

    # ---- Part F ----
    blocks.append({
        "type": "task", "num": "F", "title": "Catch the Finals Game",
        "body": (
            "<p><strong>Instructions:</strong> Tell your partner <strong>two things you own</strong>. Your partner "
            "holds up one finger for every plural /s/, /z/, or /ɪz/ they hear — 1 point per sound. Dropped sound? "
            "Say it again! Then swap.</p>"
            "<p><strong>1.</strong> I have ______. &nbsp; My score: <span class='label-box'></span></p>"
            "<p><strong>2.</strong> I have ______. &nbsp; My score: <span class='label-box'></span></p>"
        ),
    })

    # ---- Part G ----
    blocks.append({
        "type": "task", "num": "G", "title": "Florence's Recording: Tick or Cross",
        "body": (
            "<p><strong>Instructions:</strong> Listen to Florence talking about her life. The numbered underlined "
            "words end with a plural <strong>/s/</strong>, <strong>/z/</strong>, or <strong>/ɪz/</strong>. For each "
            "numbered word, write <strong>&#10003;</strong> if Florence pronounces the plural correctly, or "
            "<strong>&#10007;</strong> if she drops it.</p>"
            "<div class='task-subbox'><div class='sub-head'>Florence's transcript</div>"
            "<div class='transcript'>" + FLORENCE_TRANSCRIPT + "</div></div>"
        ),
    })

    # ---- Part H ----
    blocks.append({
        "type": "task", "num": "H", "title": "Model Reading: Partner Check",
        "body": (
            "<p><strong>Instructions:</strong> Listen to the model reading of the paragraph. Then take turns reading "
            "it to your partner. The numbered underlined words end with a plural <strong>/s/</strong>, <strong>/z/</strong>, "
            "or <strong>/ɪz/</strong>. Your partner writes <strong>&#10003;</strong> if you pronounce the plural "
            "correctly, or <strong>&#10007;</strong> if you drop it.</p>"
            "<div class='task-subbox'><div class='sub-head'>Model reading</div>"
            "<div class='transcript'>" + MODEL_READING + "</div></div>"
        ),
    })

    # ---- Answer key ----
    blocks.append({"type": "page_break"})
    blocks.append({
        "type": "task", "num": "\u2014", "title": "Answer Key (Teacher)",
        "body": (
            "<p><strong>Part A:</strong> 3 plural sounds — <em>books</em> (/s/), <em>dogs</em> (/z/), "
            "<em>glasses</em> (/ɪz/).</p>"
            "<p><strong>Part B:</strong> 1. books/book — &#10007; &nbsp; 2. dogs/dog — &#10007; &nbsp; "
            "3. glasses/glass — &#10007; &nbsp; 4. friends/friend — &#10007; &nbsp; 5. years/year — &#10007;. "
            "Pattern &#10007;&#10007;&#10007;&#10007;&#10007; — all dropped.</p>"
            "<p><strong>Part C:</strong> [answers require teacher audition — listen to the discrimination track and "
            "verify each tick/cross].</p>"
            "<p><strong>Part D syllables:</strong> books = 1, dogs = 1, glasses = 2, friends = 1.</p>"
            "<p><strong>Part E:</strong> 1. books &nbsp; 2. dogs &nbsp; 3. yes — <em>glasses</em> has 2 syllables, "
            "<em>glass</em> has 1.</p>"
            "<p><strong>Game:</strong> 1 point per heard plural /s/, /z/, or /ɪz/; do-over until the sound is heard.</p>"
            "<p><strong>Part G (Florence's transcript):</strong> &#10003; = pronounced correctly, &#10007; = plural dropped. "
            "<strong>Answers require teacher audition.</strong> Florence's feedback notes she \"sometimes drops the 's' "
            "at the end of plural words\" — the key must be verified by listening to florence-33171.m4a. 7 targets: "
            "[0] years (example, not scored) &middot; [1] hours &middot; [2] things &middot; [3] friends &middot; "
            "[4] books &middot; [5] pictures &middot; [6] books &middot; [7] plants.</p>"
            "<p><strong>Part H (Model reading):</strong> 11 targets: [1] things (/z/) &middot; [2] books (/s/) &middot; "
            "[3] dogs (/z/) &middot; [4] glasses (/ɪz/) &middot; [5] friends (/z/) &middot; [6] games (/z/) &middot; "
            "[7] siblings (/z/) &middot; [8] things (/z/) &middot; [9] plants (/z/) &middot; [10] pictures (/z/) &middot; "
            "[11] things (/z/).</p>"
        ),
    })

    return blocks


def render_worksheet(out_path: Path):
    blocks = build_blocks()
    # Resolve the cartoon src for the Part A fig_row so it sits on page 1.
    for block in blocks:
        if block.get("type") == "fig_row":
            block["src"] = opaque_asset(ILLO)
    html = Template(TEMPLATE.read_text(encoding="utf-8")).render(
        title="Pronunciation Noticing: Plural -s  /s/  /z/  /ɪz/",
        subtitle="",
        level="M2A/M3A",
        blocks=blocks,
        # resolve relative asset srcs to opaque file:// URIs
        masthead_left=opaque_asset(LOGOS["masthead_left"]),
        masthead_right=opaque_asset(LOGOS["masthead_right"]),
    )
    html = (
        html.replace("ASSETS/cambridge.png", opaque_asset(LOGOS["masthead_left"]))
        .replace("ASSETS/ACT.png", opaque_asset(LOGOS["masthead_right"]))
    )

    tmp_html = out_path.with_suffix(".html")
    tmp_html.write_text(html, encoding="utf-8")
    print(f"  [html] {tmp_html.name}")

    subprocess.run(
        ["node", str(RENDER_PDF_JS), str(tmp_html), str(out_path)],
        check=True, timeout=90,
    )
    tmp_html.unlink(missing_ok=True)
    print(f"  [pdf]  {out_path.name}")


def main():
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    render_worksheet(PDF_DIR / "Plural-s-Noticing-Worksheet.pdf")


if __name__ == "__main__":
    main()
