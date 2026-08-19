"""generate_worksheet.py — Interview Power: Answer with PREP (M2/M3, CEFR B1).

Practice worksheet for the MUIDS / international-school interview lesson.
Teaches the PREP answer structure (Position → Reason → Example → Position):

  Part A — Put the answer in order   (controlled: rebuild a PREP answer)
  Part B — Complete the frames       (controlled: linker frames from a word bank)
  Part C — Write your own PREP answer (freer: build a full answer to a new question)

Banner: PROJECTS/INTERVIEW SPEAKING/assets/interview-banner.jpg (full-width,
edge-to-edge via styles_override per the AGENTS.md .ws-image gotcha).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".kilo" / "skills" / "write-test-worksheet" / "scripts"))
from render import render_worksheet

LABEL = '<span class="label-box"></span>'
LINE = '<span style="display:inline-block;border-bottom:1.5pt solid #222;min-width:24em">&nbsp;</span>'

STYLES = """body {
  font-family: Roboto, Arial, Helvetica, sans-serif;
  font-size: 14pt;
  line-height: 1.42;
  color: #222;
  margin: 0;
  padding: 0;
}

.masthead {
  display: grid;
  grid-template-columns: 0.8fr 1.4fr 0.8fr;
  align-items: center;
  margin-bottom: 0.15em;
}
.masthead-left { text-align: left; }
.masthead-left img { height: 1.6cm; }
.masthead-center { text-align: center; font-size: 16pt; font-weight: bold; letter-spacing: 0.5pt; }
.masthead-right { text-align: right; }
.masthead-right img { height: 1.0cm; }
.masthead-sep { border: none; border-top: 1.5pt solid #000; margin: 0 0 0.25em 0; }

h1 {
  font-size: 20pt;
  text-align: center;
  margin: 0 0 0.15em 0;
}
h2 {
  font-size: 14pt;
  margin: 0.75em 0 0.25em 0;
  padding: 0.1em 0.5em;
  background: #222;
  color: #fff;
}
h3 {
  font-size: 14pt;
  margin: 0.45em 0 0.15em 0;
  color: #222;
}

.cefr-tag {
  text-align: center;
  font-size: 14pt;
  color: #555;
  margin: 0 0 0.2em 0;
}

.instructions {
  page-break-inside: avoid;
  font-size: 14pt;
  color: #444;
  margin: 0.2em 0 0.3em 0;
  padding: 0.2em 0.5em;
  background: #f0f0f0;
  border-left: 3pt solid #222;
}

.task1-sentence, .join-item, .gap-sentence {
  page-break-inside: avoid;
  margin: 0.45em 0 0 0;
  text-align: left;
}
.s-num {
  font-weight: bold;
  margin-right: 0.3em;
}
.s-text {
  font-size: 14pt;
  line-height: 1.4;
}

.mcq {
  page-break-inside: avoid;
  margin: 0.45em 0 0 0;
  text-align: left;
}
.mcq-prompt {
  font-size: 14pt;
  line-height: 1.4;
}
.mcq-options {
  margin: 0.15em 0 0 1.8em;
}
.mcq-option {
  font-size: 14pt;
  line-height: 1.35;
}

.label-box {
  display: inline-block;
  width: 2.2em;
  height: 1.4em;
  border: 1.5pt solid #222;
  margin-left: 0.6em;
  vertical-align: middle;
}

.boxed {
  display: inline-block;
  border: 1.5pt solid #222;
  background: #e8e8e8;
  padding: 0.05em 0.2em;
  font-weight: bold;
  color: #222;
}

.word-bank {
  margin: 0.35em 0 0.4em 0;
  text-align: center;
}
.bank-word {
  display: inline-block;
  border: 1pt solid #222;
  padding: 0.1em 0.7em;
  margin: 0.15em 0.2em;
  font-size: 14pt;
  background: #f7f7f7;
}

.write-lines {
  margin: 0.3em 0 0 0;
}
.write-lines .wl {
  border-bottom: 1pt solid #999;
  height: 2.0em;
}

.writing-prompt {
  font-size: 14pt;
  color: #444;
  margin: 0.4em 0 0.4em 0;
  padding: 0.3em 0.5em;
  background: #f0f0f0;
  border: 1pt solid #999;
}

.highlight-bar {
  font-size: 15pt;
  font-weight: bold;
  text-align: center;
  color: #222;
  background: #ffdd00;
  border: 1pt solid #222;
  margin: 0.5em 0 0.3em 0;
  padding: 0.35em 0.5em;
}

.ws-image {
  text-align: center;
  margin: 0.5em 0 0.4em 0;
}
.ws-image img {
  width: 100%;
  height: auto;
  object-fit: contain;
  border: 1px solid #999;
}
.ws-caption {
  font-size: 11pt;
  color: #555;
  margin-top: 0.15em;
}

.transcript {
  line-height: 2.2;
  font-size: 13pt;
  text-align: left;
  background: #fff;
  padding: 0.2em 0.4em;
}

.page-break {
  page-break-before: always;
}
"""

FORMULA = (
    "<strong>The PREP formula</strong>"
    '<table style="width:100%;border-collapse:collapse;margin-top:0.3em">'
    '<tr><th style="text-align:left;padding:0.1em 0.4em;border-bottom:1pt solid #222;white-space:nowrap">'
    "<strong>P</strong> — Position</th>"
    '<td style="padding:0.1em 0.4em;border-bottom:1pt solid #999">'
    "Say your opinion <strong>first</strong>. <em>In my opinion&hellip; / I think&hellip;</em></td></tr>"
    '<tr><th style="text-align:left;padding:0.1em 0.4em;border-bottom:1pt solid #222;white-space:nowrap">'
    "<strong>R</strong> — Reason</th>"
    '<td style="padding:0.1em 0.4em;border-bottom:1pt solid #999">'
    "Give <strong>one reason</strong>. <em>One reason is&hellip; / Because&hellip;</em></td></tr>"
    '<tr><th style="text-align:left;padding:0.1em 0.4em;border-bottom:1pt solid #222;white-space:nowrap">'
    "<strong>E</strong> — Example</th>"
    '<td style="padding:0.1em 0.4em;border-bottom:1pt solid #999">'
    "Give <strong>an example or detail</strong>. <em>For example&hellip; / In my school&hellip;</em></td></tr>"
    '<tr><th style="text-align:left;padding:0.1em 0.4em;white-space:nowrap">'
    "<strong>P</strong> — Position</th>"
    '<td style="padding:0.1em 0.4em">'
    "<strong>Repeat your opinion</strong>. <em>That&rsquo;s why I think&hellip;</em></td></tr>"
    "</table>"
)

content = {
    "title": "Interview Power — Answer with PREP",
    "cefr_tag": "M2 · M3 · CEFR B1 · Interview Speaking",
    "sections": [
        {
            "type": "image",
            "src": "PROJECTS/INTERVIEW SPEAKING/assets/interview-banner.jpg",
            "alt": "A student preparing for a school interview",
            "caption": "",
        },
        {"type": "heading", "text": "The PREP Formula"},
        {
            "type": "instructions",
            "text": "Interviewers ask short questions, but they want long answers. "
                    "Use PREP to build a strong answer, every time.",
        },
        {"type": "writing_prompt", "text": FORMULA},
        {"type": "heading", "text": "Part A — Put the Answer in Order"},
        {
            "type": "instructions",
            "text": "<strong>The question:</strong> Should mobile phones be banned at school? "
                    "The answer below is mixed up. Write the best order "
                    "(<strong>1</strong> = first, <strong>4</strong> = last) in each box.",
        },
        {
            "type": "task1_sentence",
            "items": [
                {"num": 1, "text": f"{LABEL} That&rsquo;s why I think phones should stay at school."},
                {"num": 2, "text": f"{LABEL} For example, students can look up information quickly in class."},
                {"num": 3, "text": f"{LABEL} One reason is that phones help students learn."},
                {"num": 4, "text": f"{LABEL} In my opinion, phones should be allowed at school."},
            ],
        },
        {"type": "heading", "text": "Part B — Complete the Frames"},
        {
            "type": "instructions",
            "text": "Complete each sentence with the best phrase from the box. "
                    "Use each phrase <strong>once</strong>.",
        },
        {
            "type": "word_bank",
            "words": ["In my opinion,", "One reason is", "For example,", "That&rsquo;s why"],
        },
        {
            "type": "gap_sentence",
            "items": [
                {"num": 1, "text": "____________________, homework should not be too much."},
                {"num": 2, "text": "____________________ that students need free time to rest and play."},
                {"num": 3, "text": "____________________, in my school we get homework for every subject every night."},
                {"num": 4, "text": "____________________ I believe schools should think again about homework."},
            ],
        },
        {"type": "heading", "text": "Part C — Write Your Own PREP Answer"},
        {
            "type": "instructions",
            "text": "Choose <strong>one</strong> question. Write your answer using the PREP formula. "
                    "Answer first. Then build your reason, example, and finish.",
        },
        {
            "type": "writing_prompt",
            "text": "Question 1: Should students wear school uniforms?<br>"
                    "Question 2: Is social media good for teenagers?",
        },
        {
            "type": "writing_prompt",
            "text": (
                "<strong>Position:</strong> In my opinion, " + LINE + "<br>"
                "<strong>Reason:</strong> One reason is " + LINE + "<br>"
                "<strong>Example:</strong> For example, " + LINE + "<br>"
                "<strong>Position:</strong> That&rsquo;s why " + LINE
            ),
        },
        {"type": "writing_lines", "lines": 6},
        {"type": "page_break"},
        {"type": "heading", "text": "Answer Key (Teacher)"},
        {
            "type": "writing_prompt",
            "text": (
                "<strong>Part A — Put the answer in order:</strong> "
                "Correct order: <strong>4, 3, 2, 1</strong>.<br>"
                "4 = P (In my opinion, phones should be allowed at school.) &nbsp;"
                "3 = R (One reason is that phones help students learn.) &nbsp;"
                "2 = E (For example, students can look up information quickly in class.) &nbsp;"
                "1 = P (That&rsquo;s why I think phones should stay at school.)<br><br>"
                "<strong>Part B — Complete the frames:</strong> "
                "1. In my opinion, &nbsp; 2. One reason is &nbsp; 3. For example, &nbsp; 4. That&rsquo;s why<br><br>"
                "<strong>Part C — Model answer (uniforms):</strong><br>"
                "In my opinion, students should wear school uniforms. "
                "One reason is that uniforms make everyone feel equal. "
                "For example, nobody can be judged by their clothes. "
                "That&rsquo;s why I think uniforms are a good idea for schools."
            ),
        },
    ],
}

render_worksheet(content, Path("PROJECTS/INTERVIEW SPEAKING/Interview-Power-PREP-Worksheet.pdf"), styles_override=STYLES)
print("Worksheet generated")
