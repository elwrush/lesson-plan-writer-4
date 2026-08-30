"""Generate the Rome Book Review noticing worksheet (authentic listening).

Rome (student 33168) reviewed The Phantom of the Opera; his examiner flagged
dropped final /t/, /d/ and /ɪd/ sounds (called, would, friend, complicated).
The transcript is corrected so every past t/d/id word is in the right tense;
those words are underlined. Students listen to the audio and circle the ending
letters when Rome drops the sound, or tick them when he pronounces it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_worksheet import STYLES, TRANSCRIPT_NUMBERED  # noqa: E402

sys.path.insert(0, str(Path.home() / ".kilo" / "skills" / "write-test-worksheet" / "scripts"))
from render import render_worksheet, load_template, load_logos  # noqa: E402
from worksheet_content import WorksheetContent  # noqa: E402

content = {
    "title": "Noticing — Rome's Book Review",
    "cefr_tag": "CEFR B1 · Listening · Past tense /t/ /d/ /ɪd/",
    "sections": [
        {
            "type": "instructions",
            "text": "<strong>Instructions:</strong> Listen to Rome's book review of <em>The Phantom of the Opera</em>. The underlined words end with a /t/, /d/, or /ɪd/ sound in the past. Rome sometimes drops these final sounds. Listen and <strong>circle the ending letters (t, d, or ed)</strong> when Rome does <strong>NOT</strong> say them. Put a <strong>✓</strong> when you hear the ending clearly.",
        },
        {"type": "writing_prompt", "text": TRANSCRIPT_NUMBERED},
        {"type": "page_break"},
        {"type": "heading", "text": "Answer Key (Teacher)"},
        {
            "type": "writing_prompt",
            "text": "Students tick (✓) each numbered word when Rome pronounces the final /t/, /d/, or /ɪd/ sound correctly, and cross (✗) it when he drops it.<br><br><strong>Definitive key (from the audio):</strong> only [5], [10], [22] and [23] are correct — the other 20 are dropped.<br><br>Full key: [0] ✗ · [1] ✗ · [2] ✗ · [3] ✗ · [4] ✗ · [5] ✓ · [6] ✗ · [7] ✗ · [8] ✗ · [9] ✗ · [10] ✓ · [11] ✗ · [12] ✗ · [13] ✗ · [14] ✗ · [15] ✗ · [16] ✗ · [17] ✗ · [18] ✗ · [19] ✗ · [20] ✗ · [21] ✗ · [22] ✓ · [23] ✓.<br><br>[0] <em>called</em> is the example item — present tense, not a past target. Non-target grammar is left exactly as Rome said it; only the underlined t/d/id endings are corrected.",
        },
    ],
}

def render() -> None:
    output = Path("PROJECTS/PRONUNCIATION NOTICING/Rome-Book-Review-Noticing-Worksheet.pdf")
    render_worksheet(content, output, styles_override=STYLES)
    print(f"Rendered: {output}")

    html_output = Path("PROJECTS/PRONUNCIATION NOTICING/rome-noticing.html")
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
