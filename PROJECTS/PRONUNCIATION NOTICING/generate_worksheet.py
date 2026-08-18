"""Generate the Pronunciation Noticing worksheet (Shape L) for M2A/M3A.

Renders via the write-test-worksheet skill's render_worksheet() with the
standard C·E·L Mathayom masthead and the project splash banner.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".kilo" / "skills" / "write-test-worksheet" / "scripts"))
from render import render_worksheet, load_template, load_logos
from worksheet_content import WorksheetContent

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
  margin-bottom: 0.1em;
}
.masthead-left { text-align: left; }
.masthead-left img { height: 1.6cm; }
.masthead-center { text-align: center; font-size: 16pt; font-weight: bold; letter-spacing: 0.5pt; }
.masthead-right { text-align: right; }
.masthead-right img { height: 1.0cm; }
.masthead-sep { border: none; border-top: 1.5pt solid #000; margin: 0 0 0.15em 0; }

h1 {
  font-size: 20pt;
  text-align: center;
  margin: 0 0 0 0;
}
h2 {
  font-size: 14pt;
  margin: 0.3em 0 0.1em 0;
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
  margin: 0 0 0.1em 0;
}

.instructions {
  page-break-inside: avoid;
  font-size: 14pt;
  color: #444;
  margin: 0.08em 0 0.15em 0;
  padding: 0.2em 0.5em;
  background: #f0f0f0;
  border-left: 3pt solid #222;
}

.task1-sentence, .join-item, .gap-sentence {
  page-break-inside: avoid;
  margin: 0.18em 0 0 0;
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
  margin: 0.35em 0 0 0;
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
  margin: 0.2em 0 0.3em 0;
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
  margin: 0.2em 0 0 0;
}
.write-lines .wl {
  border-bottom: 1pt solid #999;
  height: 2.0em;
}

.writing-prompt {
  font-size: 14pt;
  color: #444;
  margin: 0.2em 0 0.2em 0;
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
  margin: 0.3em 0 0.15em 0;
  padding: 0.35em 0.5em;
}

.ws-image {
  text-align: center;
  margin: 0.15em 0 0.2em 0;
}
.ws-image img {
  width: 100%;
  height: auto;
  object-fit: contain;
  border: 1pt solid #999;
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

TRANSCRIPT = (
    "Hello, my name is Rome, and today I'm going to talk about the book I want to recommend. "
    "It is [0] called The Phantom of the Opera by Gaston Leroux."
    "<br><br>What <u>would</u> you do if you were an famous opera singer who <u>wanted</u> to marry your "
    "childhood <u>friend</u> but marrying your childhood <u>friend</u> <u>would</u> mean you have to end "
    "your own career? The story takes place in 1880s at the Palais Garnier opera theater in, in Paris. "
    "There was a little girl who's name is Christine Daaé. She was a ballet, ballet dancer who's become "
    "very popular after replacing the, the lead soprano because of her good teacher who she <u>called</u> "
    "the Angel of Music. And one day... she <u>liked</u> performing like normal but her childhood "
    "<u>friend</u>, like, who she didn't see, like, for many years and, and, and <u>wanted</u> to marry "
    "her and but marry her <u>would</u> mean she <u>had</u> to end her own career. So the, her teacher "
    "who's revealed to be Erik got very angry and <u>killed</u> innocent people then <u>kidnapped</u> "
    "Christine to his lair below the, below the opera theater. So her childhood <u>friend</u> Raoul "
    "<u>attempted</u> to rescue her but <u>ended</u> up in a death trap. So Erik <u>decided</u>, if you "
    "want to save your childhood <u>friend</u> you have to choose me and if you choose Raoul, Raoul "
    "<u>would</u> die. So, so instead of choosing Raoul and kill him, she choose the phantom or the Erik. "
    "Then Erik got very, very, very confused, like, I <u>had</u> never seen a person with, with this "
    "kindness before and he, like, wow, and then ... ... and then, like, <u>disappeared</u> and let, and "
    "let Christine and Raoul go."
    "<br><br>I really like this story because it, it was very <u>complicated</u> and, and the thing I "
    "like the most is when Raoul choose the strategy of, of Erik to kill a innocent people he cut the "
     "rope of the chandelier and let it boom, [laugh] and let it fall down. And, and the thing I don't "
    "like is in the end the, you know, human feeling is very <u>complicated</u> and I don't know why "
    "Erik choose to let them both go. Thank you."
)


def number_targets(text: str) -> str:
    """Prefix each underlined target with [n] in order of appearance."""
    counter = {"n": 0}

    def repl(_match: re.Match) -> str:
        counter["n"] += 1
        return f"[{counter['n']}] <u>"

    return re.sub(r"<u>", repl, text)


TRANSCRIPT_NUMBERED = number_targets(TRANSCRIPT)

QUANTUM = (
    "Quantum physics sounds strange. It <u>started</u> as a simple question: scientists <u>wanted</u> "
    "answers about light, so they <u>studied</u> and <u>decided</u> how one particle <u>could</u> "
    "<u>act</u> as a wave. They <u>discovered</u> something amazing. <u>Light</u> exists in two "
    "states at once. This idea <u>changed</u> our <u>world</u>. Computers, phones, and lasers "
    "<u>needed</u> this discovery. So remember, when you use your phone, you are using quantum physics!"
)

QUANTUM_NUMBERED = number_targets(QUANTUM)

content = {
    "title": "Pronunciation Noticing: Final /t/, /d/ and /Id/",
    "cefr_tag": "CEFR B1 · Noticing · M2A / M3A",
    "sections": [
        {
            "type": "image",
            "src": "PROJECTS/PRONUNCIATION NOTICING/assets/banner.jpg",
            "alt": "Gaming at night",
            "caption": "",
        },
        {"type": "heading", "text": "Part A — Listen. Can You Hear It?"},
        {
            "type": "instructions",
            "text": "<strong>Instructions:</strong> Listen to the two recordings. One is Thai-style English. One is native English. In the native version, every word ends with its full sound. Tap your finger every time you hear a final <strong>/t/</strong> or <strong>/d/</strong> sound.",
        },
        {
            "type": "writing_prompt",
            "text": "<strong>Model sentence:</strong> I started my game at eight and played it all night.",
        },
        {
            "type": "task1_sentence",
            "items": [
                {"num": 1, "text": "How many final /t/ or /d/ sounds did you hear? Write the number: <span class=\"label-box\"></span>"}
            ],
        },
        {"type": "heading", "text": "Part B — Same or Different?"},
        {
            "type": "instructions",
            "text": "<strong>Instructions:</strong> Listen to the recording. After each number you will hear a word <strong>twice</strong>. Are both pronounced correctly, or is the final sound missing the second time? Write <strong>✓</strong> if both are correct, or <strong>✗</strong> if the final sound is dropped.",
        },
        {
            "type": "task1_sentence",
            "items": [
                {"num": 1, "text": "<span class=\"label-box\"></span> night"},
                {"num": 2, "text": "<span class=\"label-box\"></span> fight"},
                {"num": 3, "text": "<span class=\"label-box\"></span> last"},
                {"num": 4, "text": "<span class=\"label-box\"></span> wanted"},
                {"num": 5, "text": "<span class=\"label-box\"></span> played"},
            ],
        },
        {"type": "heading", "text": "Part C — Past Tense or Not?"},
        {
            "type": "instructions",
            "text": "<strong>Instructions:</strong> Listen to the recording. After each number you will hear a verb. Each one is written below in the past tense with -ed. Is the -ed ending pronounced? Write <strong>✓</strong> if you hear it, or <strong>✗</strong> if the ending is missing.",
        },
        {
            "type": "task1_sentence",
            "items": [
                {"num": 1, "text": "<span class=\"label-box\"></span> wanted"},
                {"num": 2, "text": "<span class=\"label-box\"></span> played"},
                {"num": 3, "text": "<span class=\"label-box\"></span> stopped"},
                {"num": 4, "text": "<span class=\"label-box\"></span> needed"},
                {"num": 5, "text": "<span class=\"label-box\"></span> watched"},
                {"num": 6, "text": "<span class=\"label-box\"></span> stayed"},
                {"num": 7, "text": "<span class=\"label-box\"></span> started"},
                {"num": 8, "text": "<span class=\"label-box\"></span> helped"},
            ],
        },
        {"type": "heading", "text": "Part D — The -ed Pattern"},
        {
            "type": "instructions",
            "text": "<strong>Instructions:</strong> Say each word and clap the syllables. Write the number of syllables next to the word.",
        },
        {
            "type": "gap_sentence",
            "items": [
                {"num": 1, "text": "wanted  ______  syllables"},
                {"num": 2, "text": "played  ______  syllables"},
                {"num": 3, "text": "stopped  ______  syllables"},
                {"num": 4, "text": "needed  ______  syllables"},
            ],
        },
        {
            "type": "writing_prompt",
            "text": "<strong>Rule:</strong> After /t/ or /d/, -ed sounds like <strong>/ɪd/</strong> and adds one syllable: <em>wanted</em> = 3. After other sounds it is <strong>/t/</strong> or <strong>/d/</strong>: <em>played</em> = 1, <em>stopped</em> = 1. Dropped finals hide the past tense — <em>want</em> is present, <em>wanted</em> is past!",
        },
        {"type": "heading", "text": "Part E — Does the Ending Matter?"},
        {
            "type": "instructions",
            "text": "<strong>Instructions:</strong> Circle the correct past tense word, then answer the question.",
        },
        {
            "type": "task1_sentence",
            "items": [
                {"num": 1, "text": "Circle the past tense: Last night I (want / wanted) to play my game."},
                {"num": 2, "text": "Circle the past tense: I (play / played) it all night."},
                {"num": 3, "text": "Does <em>night</em> end with a /t/ sound? <span class=\"label-box\"></span>  yes / no"},
            ],
        },
        {"type": "highlight_bar", "text": "Main Activity — Catch the Finals"},
        {"type": "heading", "text": "Part F — Catch the Finals Game"},
        {
            "type": "instructions",
            "text": "<strong>Instructions:</strong> Tell your partner <strong>two things you did last night</strong>. Your partner holds up one finger for every final /t/ or /d/ they hear — 1 point per sound. Dropped sound? Say it again! Then swap.",
        },
        {
            "type": "join_item",
            "items": [
                {"num": 1, "text": "I ______ last night.  My score: <span class=\"label-box\"></span>", "lines": 1},
                {"num": 2, "text": "I ______ last night.  My score: <span class=\"label-box\"></span>", "lines": 1},
            ],
        },
        {"type": "heading", "text": "Part G — Rome's Book Review: Tick or Cross"},
        {
            "type": "instructions",
            "text": "<strong>Instructions:</strong> Listen to Rome's book review of <em>The Phantom of the Opera</em>. The numbered underlined words end with a final <strong>/t/</strong>, <strong>/d/</strong>, or <strong>/ɪd/</strong> sound. For each numbered word, write <strong>✓</strong> if Rome pronounces the final sound correctly, or <strong>✗</strong> if he drops it.",
        },
        {
            "type": "writing_prompt",
            "text": "<div class=\"transcript\">" + TRANSCRIPT_NUMBERED + "</div>",
        },
        {"type": "heading", "text": "Part H — Quantum Theory: Partner Check"},
        {
            "type": "instructions",
            "text": "<strong>Instructions:</strong> Listen to the model reading of the paragraph. Then take turns reading it to your partner. The numbered underlined words end with a final <strong>/t/</strong>, <strong>/d/</strong>, or <strong>/ɪd/</strong> sound. Your partner writes <strong>✓</strong> if you pronounce the ending correctly, or <strong>✗</strong> if you drop it.",
        },
        {
            "type": "writing_prompt",
            "text": "<div class=\"transcript\">" + QUANTUM_NUMBERED + "</div>",
        },
        {"type": "page_break"},
        {"type": "heading", "text": "Answer Key (Teacher)"},
        {
            "type": "writing_prompt",
            "text": "<strong>Part A:</strong> 5 final sounds — <em>started</em> (/ɪd/), <em>eight</em> (/t/), <em>played</em> (/d/), <em>it</em> (/t/), <em>night</em> (/t/).<br><strong>Part B:</strong> Audio track (Helen announces numbers, Benedict says each word twice): 1. night / nigh — ✗ &nbsp; 2. fight / fight — ✓ &nbsp; 3. last / las — ✗ &nbsp; 4. wanted / wonty — ✗ &nbsp; 5. played / played — ✓. Pattern ✗✓✗✗✓ — no rhythm to lock onto.<br><strong>Part C:</strong> 1. wanted ✓ (/wɒntɪd/) · 2. played ✗ (heard 'play') · 3. stopped ✓ (/stɒpt/) · 4. needed ✗ (heard 'need') · 5. watched ✓ (/wɒtʃt/) · 6. stayed ✓ (/steɪd/) · 7. started ✗ (heard 'start') · 8. helped ✓ (/helpt/). The dropped words lose the whole -ed syllable.<br><strong>Part D syllables:</strong> wanted = 3, played = 1, stopped = 1, needed = 2.<br><strong>Part E:</strong> 1. wanted &nbsp; 2. played &nbsp; 3. yes — <em>night</em> ends with /t/.<br><strong>Game:</strong> 1 point per heard final /t/ or /d/; do-over until the release is heard.<br><strong>Part G (Rome's transcript):</strong> ✓ = pronounced correctly, ✗ = final sound dropped. <strong>Only [5], [10], [22] and [23] are correct — the other 20 are dropped.</strong> Full key: [0] ✗ · [1] ✗ · [2] ✗ · [3] ✗ · [4] ✗ · [5] ✓ · [6] ✗ · [7] ✗ · [8] ✗ · [9] ✗ · [10] ✓ · [11] ✗ · [12] ✗ · [13] ✗ · [14] ✗ · [15] ✗ · [16] ✗ · [17] ✗ · [18] ✗ · [19] ✗ · [20] ✗ · [21] ✗ · [22] ✓ · [23] ✓. [0] <em>called</em> is the example item — present tense, not a past target. Non-target grammar is untouched. Audio: slides/assets/rome-book-review.mp3.<br><strong>Part H (Quantum partner check):</strong> No fixed answers — the partner judges live. the model reading (slides/assets/quantum-model.mp3) is the reference; replay it to settle disagreements. 11 targets: [1] started (/ɪd/) · [2] wanted (/ɪd/) · [3] studied (/d/) · [4] decided (/ɪd/) · [5] could (/d/) · [6] act (/t/) · [7] discovered (/d/) · [8] light (/t/) · [9] changed (/d/) · [10] needed (/ɪd/) · [11] world (/d/).",
        },
    ],
}

def render() -> None:
    output = Path("PROJECTS/PRONUNCIATION NOTICING/Pronunciation-Noticing-Final-t-d-Worksheet.pdf")
    render_worksheet(content, output, styles_override=STYLES)
    print(f"Rendered: {output}")

    html_output = Path("PROJECTS/PRONUNCIATION NOTICING/worksheet.html")
    validated = WorksheetContent.model_validate(content)
    logos = load_logos()
    template = load_template("worksheet")
    html_output.write_text(
        template.render(content=validated, styles=STYLES,
                        logo_left_data_uri=logos["logo_left_data_uri"],
                        logo_right_data_uri=logos["logo_right_data_uri"]),
        encoding="utf-8",
    )
    print(f"HTML dump: {html_output}")


if __name__ == "__main__":
    render()
