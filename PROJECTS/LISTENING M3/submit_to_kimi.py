"""submit_to_kimi.py — Send the It's Academic dialog draft to Kimi to write the final version.

Reads dialog-draft.md (context + Chunk structure) and asks kimi-k3 to produce a
polished final B2 dialog for the two-voice history podcast, keeping the 4-chunk
structure and the established facts, plus 8 dictation questions.

Credentials come from MOONSHOT_API_KEY in the interactive shell (run via
`zsh -ic 'python ...'`). Output is written to dialog_kimi.md.
"""

import os
import sys
from pathlib import Path

from openai import OpenAI

HERE = Path(__file__).resolve().parent
DRAFT = HERE / "dialog-draft.md"
OUT = HERE / "dialog_kimi.md"

MODEL = "kimi-k3"
BASE_URL = "https://api.moonshot.ai/v1"


SYSTEM = (
    "You are a professional educational podcast scriptwriter and a history "
    "teacher. You write warm, funny, upbeat B2-level dialogue for smart "
    "teenagers. You never invent false historical facts. You keep the "
    "structure, characters, and all facts the user gives you, but you make "
    "the language sharper, funnier, and more natural to listen to."
)

USER = """Rewrite and polish the following draft history-podcast dialog into the final
listen-ready version.

SCRIPT AIMS:
- Two voices: Jack Smith (host, adult, warm + funny) and Ebony Mills (teen
  researcher, sharp, upbeat American teenage girl).
- CEFR B2 for smart Thai middle-schoolers. Fun, upbeat, conversational punch.
- Keep the SAME 4-chunk structure. Do NOT reorder or drop any chunk.
- Keep ALL the historical facts exactly as given (dates, treaty names, names,
  figures). Do not add new unsupported facts.
- ~10% longer than the draft is fine; make it feel like a real radio show with
  energy, light banter, and clear mini "so what" takeaways at the end of each
  chunk.

THEN, at the very end, add a section titled "DICTATION QUESTIONS" with exactly
8 listening-comprehension questions (2 per chunk, ordered 1-8). These are the
questions students will hear and write during the dictation, then answer after
listening to each part. Make them B2-appropriate and answerable from the dialog.

BEGIN DRAFT
{draft}
END DRAFT

Output the FINAL dialog (markdown, speaker names bolded "**Speaker:**") followed
by the "## DICTATION QUESTIONS" section. Output the dialog only, no commentary.
"""


def main() -> None:
    api_key = os.environ.get("MOONSHOT_API_KEY")
    if not api_key:
        print("ERROR: MOONSHOT_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    draft = DRAFT.read_text(encoding="utf-8")
    client = OpenAI(api_key=api_key, base_url=BASE_URL)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER.format(draft=draft)},
        ],
        max_tokens=6000,
    )
    text = resp.choices[0].message.content.strip()
    OUT.write_text(text + "\n", encoding="utf-8")
    print(f"Kimi output written to {OUT.name}")


if __name__ == "__main__":
    main()
