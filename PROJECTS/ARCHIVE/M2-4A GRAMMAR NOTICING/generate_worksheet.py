#!/usr/bin/env python3
"""Generate the Shape S Grammar Noticing worksheet (M2-4A).

Target feature: "there is/there are" (existence) vs "it have/it has" (Thai L1
transfer of the single existential `mii`). The worksheet follows the Shape S
Noticing-First arc, mirroring the Shape L pronunciation-noticing template.

Noticing targets are numbered [0]=example, [1]-[n]=scored. Lines are drawn from
real learner writing (writing_assessment_cambridge), chosen to span six distinct
dimensions of the error:
  d1 wrong subject + "have"        (it have)
  d2 wrong subject + "has"         (it has)
  d3 correct "there" + wrong verb  (there have / there has)
  d4 "there is" + plural           (there is many)
  d5 "there are" + singular        (there are a/an)
  d6 dropped copula                (it a / it very)

Layout: project-local template (SCRIPTS/grammar_noticing_worksheet.html) — the
same C.R.A.P. format as the Plural-s noticing sheet (navy accent #1a3a5c, boxed
task headers, CEFR badge, page numbers).
"""
import re
import subprocess
import tempfile
from pathlib import Path

from jinja2 import Template

PROJECT_ROOT = Path("/mnt/c/PROJECTS/LESSON-PLAN-WRITER-4")
PROJ = PROJECT_ROOT / "PROJECTS" / "M2-4A GRAMMAR NOTICING"
TEMPLATE = PROJ / "SCRIPTS" / "grammar_noticing_worksheet.html"
PDF_DIR = PROJ
RENDER_PDF_JS = PROJECT_ROOT / "scripts" / "render-pdf.js"
LOGOS = {
    "masthead_left": PROJECT_ROOT / "ASSETS" / "cambridge.png",
    "masthead_right": PROJECT_ROOT / "ASSETS" / "ACT.png",
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


def numbered_targets(text: str, start: int = 0) -> str:
    """Number and underline the specified target spans in the noticing text.

    The author writes target phrases wrapped in <span class='target'>. Each is
    then re-wrapped with a [n] prefix. @start is the number of the FIRST span:
    pass 0 so the first span becomes the [0] example item (authentic text), or
    1 so the first span is the first scored item at [1] (model reading).
    """
    counter = {"n": start}

    def repl(m: re.Match) -> str:
        n = counter["n"]
        counter["n"] += 1
        return f"[{n}] <span class='target'>{m.group(1)}</span>"

    return re.sub(
        r"<span class='target'>(.*?)</span>",
        repl,
        text,
        flags=re.S,
    )


# ---------------------------------------------------------------------------
# Noticing text (authored verbatim from real learner writing, corrected only
# in the target feature where the noticing text should read as the *target*;
# the raw-error items live in Parts A-C.)
# ---------------------------------------------------------------------------

# The final model paragraph (Part H) — corrected to the target so students can
# compare against it. Kept neutral (a place), not reusing the story lines.
MODEL_READING = (
    "Tokyo is a great city. <span class='target'>There are</span> many places to visit "
    "and <span class='target'>there is</span> a lot of delicious food. "
    "<span class='target'>There is</span> a beautiful view and "
    "<span class='target'>there are</span> nice people. "
    "<span class='target'>There is</span> a big river and "
    "<span class='target'>there are</span> many shops. "
    "I love Tokyo because <span class='target'>there is</span> everything I need."
)

# Authentic noticing text (Part G) — verbatim from a real learner, adapted only
# so the numbered targets are the *existence* expressions. Other grammar stays as
# the student wrote it (authenticity is the point).
AUTHENTIC_TEXT = (
    "Tokyo is one of the greatest city I ever visited. "
    "<span class='target'>It have</span> a beautiful view, nice people, beautiful culture and more! "
    "Let's talk about places in Tokyo. At Shibuya "
    "<span class='target'>there have</span> a tall cylinder building, and at Harajuku "
    "<span class='target'>there have</span> a main street with many clothing shops. "
    "Tokyo is not a normal place, <span class='target'>there have</span> a vital culture "
    "and a lot of activities. <span class='target'>It have</span> everything you want in one city. "
    "And there <span class='target'>are a</span> beautiful museum too, and "
    "there <span class='target'>are a</span> giant robot that everyone wants to see."
)


def build_blocks():
    blocks = []

    # ---- Part A ---- (contrast pair: learner version vs target version)
    blocks.append({
        "type": "task",
        "num": "A",
        "title": "Notice the Difference",
        "body": (
            "<p><strong>Instructions:</strong> Read the two passages about Tokyo. "
            "One is written in the learner/transfer way. One is the target. "
            "Underline every <strong>it have / it has / there have / there has</strong> "
            "form you can find. Then answer the question.</p>"
            "<div class='task-subbox'><div class='sub-head'>Learner English</div>"
            "<p>Tokyo is a great city. <em>It have</em> many places to visit. "
            "<em>It have</em> a lot of delicious food. <em>There have</em> a beautiful view and "
            "<em>there have</em> nice people. <em>It has</em> a big river too.</p></div>"
            "<div class='task-subbox'><div class='sub-head'>Standard English</div>"
            "<p>The same city, the target way. <strong>There are</strong> many places to visit. "
            "<strong>There is</strong> a lot of delicious food. <strong>There is</strong> a beautiful view and "
            "<strong>there are</strong> nice people. <strong>There is</strong> a big river too.</p></div>"
            "<p><strong>1.</strong> How many <em>have</em> forms did you underline in the "
            "learner version? <span class='label-box'></span></p>"
            "<p><strong>2.</strong> What word replaced <em>have</em> in the standard version? "
            "<span class='label-box'></span> &nbsp; (it changed every time)</p>"
        ),
    })

    # ---- Part B ---- (Discrimination: which form fits? 6 dimensions)
    blocks.append({
        "type": "task",
        "num": "B",
        "title": "Correct or Not? (each is a real learner sentence)",
        "body": (
            "<p><strong>Instructions:</strong> Read each sentence. If the existence "
            "expression is correct, write <strong>&#10003;</strong>. If it should be "
            "<strong>there is</strong> or <strong>there are</strong>, write "
            "<strong>&#10007;</strong>. The first one is done for you.</p>"
            + label_row(0, "Tokyo is a great city. <strong>It have</strong> many places. &rarr; &#10007;")
            + label_row(1, "I prefer the cinema because <strong>it has</strong> better quality.")
            + label_row(2, "There <strong>have</strong> a lot of shopping malls in Tokyo.")
            + label_row(3, "In my area <strong>there has</strong> only one park.")
            + label_row(4, "There <strong>is</strong> many activities we can do.")
            + label_row(5, "There <strong>are</strong> a beautiful ancient city in Thailand.")
            + label_row(6, "Tokyo <strong>it</strong> very crowded and busy.")
            + label_row(7, "<strong>There are</strong> many people in Bangkok city.")
            + label_row(8, "<strong>There is</strong> a big Christmas tree at school.")
        ),
    })

    # ---- Part C ---- (Feature focus: the pattern / rule)
    blocks.append({
        "type": "task",
        "num": "C",
        "title": "The Pattern: Existence vs Possession",
        "body": (
            "<p><strong>Instructions:</strong> Read each sentence. Is the person "
            "speaking about <strong>owning</strong> something (possession), or about "
            "something that <strong>exists</strong> somewhere? Write "
            "<strong>P</strong> for possession or <strong>E</strong> for existence.</p>"
            + label_row(1, "I have a new phone.")
            + label_row(2, "There is a book on the table.")
            + label_row(3, "She has two dogs.")
            + label_row(4, "There are many shops near my school.")
            + label_row(5, "There has only one park in my area.")
            + label_row(6, "They have a big house.")
            + "<div class='rule-box'>"
            + "<p class='rule-title'><strong>The rule</strong></p>"
            + "<ul class='rule-list'>"
            + "<li><strong>HAVE</strong> = possession. You <em>own</em> it: "
            "<em>I have a cat.</em></li>"
            + "<li><strong>THERE IS / THERE ARE</strong> = existence. It <em>exists</em> "
            "somewhere: <em>There is a cat on the roof.</em></li>"
            + "<li>Thai uses one word, <strong>mi</strong>, for both. "
            "English uses two: <em>have</em> and <em>there is/are</em>.</li>"
            + "<li><strong>there is</strong> + singular / uncountable. "
            "<strong>there are</strong> + plural.</li>"
            + "</ul>"
            + "<p class='rule-foot'><em>If the sentence tells you WHERE something is or "
            "that it happens to exist — use <b>there is/are</b>, never <b>have</b>.</em></p>"
            + "</div>"
        ),
    })

    # ---- Part D ---- (Agreement: there is vs there are)
    blocks.append({
        "type": "task",
        "num": "D",
        "title": "Is or Are?",
        "body": (
            "<p><strong>Instructions:</strong> Circle the correct form. "
            "Then underline the word that helped you decide.</p>"
            "<p><strong>1.</strong> On the desk <strong>there (is / are)</strong> three books.</p>"
            "<p><strong>2.</strong> In the park <strong>there (is / are)</strong> a big tree.</p>"
            "<p><strong>3.</strong> In my bag <strong>there (is / are)</strong> some pencils.</p>"
            "<p><strong>4.</strong> On the wall <strong>there (is / are)</strong> a picture.</p>"
            "<p><strong>5.</strong> Outside the school <strong>there (is / are)</strong> many students.</p>"
            "<p><strong>6.</strong> In my street <strong>there (is / are)</strong> some shops.</p>"
        ),
    })

    # ---- Part E ---- (Controlled production: rewrite it have -> there is/are)
    blocks.append({
        "type": "task",
        "num": "E",
        "title": "Rewrite the Learner Way",
        "body": (
            "<p><strong>Instructions:</strong> Rewrite each sentence so it uses "
            "<strong>there is</strong> or <strong>there are</strong>. Make the verb "
            "agree with the noun that follows.</p>"
            "<p><strong>1.</strong> Corfu it have many beaches.<br>"
            "<span class='write-line'></span></p>"
            "<p><strong>2.</strong> Osaka there have a lot of activities.<br>"
            "<span class='write-line'></span></p>"
            "<p><strong>3.</strong> The cinema it has better quality.<br>"
            "<span class='write-line'></span></p>"
            "<p><strong>4.</strong> My area it have only one park.<br>"
            "<span class='write-line'></span></p>"
        ),
    })

    # ---- Part F ---- (Freer use: Catch the There is/are game)
    blocks.append({
        "type": "task",
        "num": "F",
        "title": "Catch the There Is / There Are",
        "body": (
            "<p><strong>Instructions:</strong> Tell your partner <strong>two things "
            "about your city or school</strong>: something that exists there and where it is. "
            "Your partner counts <strong>one point</strong> for every correct "
            "<strong>there is / there are</strong> they hear. Wrong form = do-over! Then swap.</p>"
            "<p><strong>1.</strong> In my school/city, ... &nbsp; My score: <span class='label-box'></span></p>"
            "<p><strong>2.</strong> In my school/city, ... &nbsp; My score: <span class='label-box'></span></p>"
        ),
    })

    # ---- Part G ---- (Authentic noticing: real learner passage)
    blocks.append({
        "type": "task",
        "num": "G",
        "title": "A Real Student's Writing: Tick or Cross",
        "body": (
            "<p><strong>Instructions:</strong> This is a real M2-4A student writing about "
            "Tokyo. The numbered underlined expressions use <em>have</em> or <em>there</em>. "
            "Write <strong>&#10003;</strong> if the existence form is correct, or "
            "<strong>&#10007;</strong> if it should be <strong>there is / there are</strong>.</p>"
            "<div class='task-subbox'><div class='sub-head'>Student text</div>"
            "<div class='transcript'>" + numbered_targets(AUTHENTIC_TEXT, start=0) + "</div></div>"
        ),
    })

    # ---- Part H ---- (Model reading: partner check)
    blocks.append({
        "type": "task",
        "num": "H",
        "title": "Model Reading: Partner Check",
        "body": (
            "<p><strong>Instructions:</strong> Read the model paragraph to your partner. "
            "The numbered underlined expressions use <strong>there is</strong> or "
            "<strong>there are</strong>. Your partner writes <strong>&#10003;</strong> "
            "if you say it correctly, or <strong>&#10007;</strong> if you use "
            "<em>have</em> instead.</p>"
            "<div class='task-subbox'><div class='sub-head'>Model reading</div>"
            "<div class='transcript'>" + numbered_targets(MODEL_READING, start=1) + "</div></div>"
        ),
    })

    # ---- Answer key ----
    blocks.append({"type": "page_break"})
    blocks.append({
        "type": "task",
        "num": "\u2014",
        "title": "Answer Key (Teacher)",
        "body": (
            "<p><strong>Part A:</strong> 5 <em>have</em> forms in the learner version. "
            "The word that replaced <em>have</em> every time was "
            "<strong>there is / there are</strong>.</p>"
            "<p><strong>Part B:</strong> "
            "0. &#10007; &nbsp; 1. &#10007; (there is better quality) &nbsp; "
            "2. &#10007; (there are a lot of shopping malls) &nbsp; "
            "3. &#10007; (there is only one park) &nbsp; 4. &#10007; (there are many activities) &nbsp; "
            "5. &#10007; (there is a beautiful ancient city) &nbsp; "
            "6. &#10007; (Tokyo it is very crowded / there are very crowded people) &nbsp; "
            "7. &#10003; &nbsp; 8. &#10003;.</p>"
            "<p><strong>Part C:</strong> 1. P (I own it) &nbsp; 2. E &nbsp; 3. P &nbsp; "
            "4. E &nbsp; 5. E (should be <em>there is</em>) &nbsp; 6. P. "
            "The key concept: <em>have</em> = own, <em>there is/are</em> = exists.</p>"
            "<p><strong>Part D:</strong> 1. are (books) &nbsp; 2. is (tree) &nbsp; "
            "3. are (pencils) &nbsp; 4. is (picture) &nbsp; 5. are (students) &nbsp; "
            "6. are (shops).</p>"
            "<p><strong>Part E:</strong> 1. There are many beaches in Corfu. &nbsp; "
            "2. There are a lot of activities in Osaka. &nbsp; "
            "3. There is better quality at the cinema. &nbsp; "
            "4. There is only one park in my area.</p>"
            "<p><strong>Part F:</strong> 1 point per correct <em>there is / there are</em>; "
            "do-over until the form is correct.</p>"
            "<p><strong>Part G:</strong> &#10003; = correct, &#10007; = should be "
            "<em>there is/are</em>. 0. <em>It have</em> &#10007; (example) &middot; "
            "1. <em>there have</em> &#10007; &middot; 2. <em>there have</em> &#10007; &middot; "
            "3. <em>there have</em> &#10007; &middot; 4. <em>It have</em> &#10007; &middot; "
            "5. <em>are a</em> &#10007; &middot; 6. <em>are a</em> &#10007;.</p>"
            "<p><strong>Part H (Model reading):</strong> 7 targets: [1] <em>There are</em> &middot; "
            "[2] <em>there is</em> &middot; [3] <em>There is</em> &middot; [4] <em>there are</em> &middot; "
            "[5] <em>There is</em> &middot; [6] <em>there are</em> &middot; [7] <em>there is</em>.</p>"
        ),
    })

    return blocks


def label_row(num: int, text: str) -> str:
    """One tick/cross item with a label box."""
    return f"<p style='margin:0.25em 0 0 0'><strong>{num}.</strong> <span class='label-box'></span> {text}</p>"


def render_worksheet(out_path: Path):
    blocks = build_blocks()
    html = Template(TEMPLATE.read_text(encoding="utf-8")).render(
        title="Grammar Noticing: There is / There are",
        subtitle="Existence vs possession — Thai \u2018mii\u2019 transfer",
        level="M2-4A",
        blocks=blocks,
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
    render_worksheet(PDF_DIR / "Grammar-Noticing-There-is-are-Worksheet.pdf")


if __name__ == "__main__":
    main()
