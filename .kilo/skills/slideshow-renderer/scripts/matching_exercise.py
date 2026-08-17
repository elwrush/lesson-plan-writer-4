"""
matching_exercise.py — Generate auto-animate matching exercise slides.

Usage:
    from matching_exercise import build_matching_pair

    slides = build_matching_pair(
        slide_id="match-ex4",
        title="Match the halves",
        bg_color="#052e0d",
        stems=["I thought it was a documentary,", "The movie deals with real-life issues"],
        options=["but it was completely fictional", "like homelessness and unemployment"],
        correct_order=[0, 1],  # index of correct option for each stem
    )

Returns a list of two dicts (step=1 and step=2) ready to insert into
the "slides" array of data.json.

A matching exercise is the "Controlled retrieval practice" stage of a
Shape K vocabulary lesson (see LESSON-SHAPES/shape-k.json).

Landing-page rule (learned the hard way):
  Step 1 lists the option pool in its textbook letter order — a, b, c,
  d, e … top to bottom in the right column — exactly as printed in the
  book, so students can map letters to stems. NEVER scramble the letter
  labels on step 1. Step 2 animates each option to its matched stem and
  shows the correct letter per stem (e.g. rows read b, d, c, e, a when
  the key is 1-b, 2-d, 3-c, 4-e, 5-a).
"""

_COMMON_STYLE = (
    ".match-grid{display:grid;grid-template-columns:1fr 1fr;"
    "gap:4px 12px;margin:5px 0;width:100%;font-size:32px}"
    ".match-grid .stem{color:#fff;padding:6px 4px;"
    "border-bottom:1px solid rgba(255,255,255,0.08);"
    "display:flex;align-items:center;white-space:nowrap}"
    ".match-grid .stem .num{color:#ffdd00;min-width:24px;margin-right:4px}"
    ".match-grid .opt{padding:6px 4px;"
    "border-bottom:1px solid rgba(255,255,255,0.08);"
    "display:flex;align-items:center;text-align:left;white-space:nowrap}"
    ".match-grid .opt .ltr{margin-right:6px}"
)

_SCRAMBLE_STYLE = _COMMON_STYLE + (
    ".match-grid .opt .ltr{color:#e67e22}"
)

_MATCHED_STYLE = _COMMON_STYLE + (
    ".match-grid .opt .ltr{color:#2ecc71}"
)


def _build_html(stems: list[str], options: list[str],
                order: list[int], letter_label: bool,
                style: str) -> str:
    """Build the 2-column grid HTML.

    Args:
        stems: list of stem texts
        options: list of option texts
        order: which option text goes with each stem (by index)
        letter_label: if True, prepend a,b,c... labels
        style: CSS block
    """
    rows: list[str] = []
    letters = [chr(ord("a") + i) for i in range(len(options))]

    for i, (stem_txt, opt_idx) in enumerate(zip(stems, order)):
        opt_txt = options[opt_idx]
        lbl = f'<span class="ltr">{letters[opt_idx]}</span>' if letter_label else ""
        rows.append(
            f'<div class="stem" data-id="s{i+1}">'
            f'<span class="num">{i+1}</span>{stem_txt}</div>'
            f'<div class="opt" data-id="o{opt_idx+1}">'
            f'{lbl} {opt_txt}</div>'
        )

    return f"<style>{style}</style><div class=\"match-grid\" data-id=\"grid\">" + "".join(rows) + "</div>"


def build_matching_pair(
    slide_id: str,
    title: str,
    stems: list[str],
    options: list[str],
    correct_order: list[int] | None = None,
    bg_color: str = "#052e0d",
) -> list[dict]:
    """Generate an auto-animate-pair for a matching exercise.

    Step 1 (landing) lists the option pool in textbook order — the right
    column reads a, b, c, d, e … top to bottom. Step 2 animates each
    option to its matched stem, showing the correct letter per stem.

    Args:
        slide_id: unique id for the pair (both steps share this)
        title: slide heading
        stems: left-column texts (one per row)
        options: right-column texts (the pool to match)
        correct_order: list of option indices, one per stem.
            E.g. [2, 0, 1] means stem 0 matches option 2,
            stem 1 matches option 0, stem 2 matches option 1.
            Defaults to [0, 1, 2, ...] (identity order).
        bg_color: slide background hex

    Returns:
        Two dicts [step_1, step_2] for insertion into "slides".
    """
    n = len(stems)
    if correct_order is None:
        correct_order = list(range(n))

    # Step 1: options listed in letter order (identity), so the right
    # column reads a, b, c, d, e exactly as printed in the textbook.
    # Step 2: options snapped to their correct stems (correct_order).
    step1_html = _build_html(
        stems, options, list(range(n)),
        letter_label=True, style=_SCRAMBLE_STYLE,
    )
    step2_html = _build_html(
        stems, options, correct_order,
        letter_label=True, style=_MATCHED_STYLE,
    )

    return [
        {
            "layout": "auto-animate-pair",
            "id": slide_id,
            "step": 1,
            "background_color": bg_color,
            "title": title,
            "body": step1_html,
            "notes": "Step 1: Options listed in order (a, b, c...). Ask students to match.",
        },
        {
            "layout": "auto-animate-pair",
            "id": slide_id,
            "step": 2,
            "background_color": bg_color,
            "title": title,
            "body": step2_html,
            "notes": "Step 2: Options snapped to correct positions.",
        },
    ]
