#!/usr/bin/env python3
"""build_deck.py — Build data.json for the It's Academic Opium Wars + Thailand deck.

Slide text is authored verbatim as literal strings below; helpers only wire
structure (layout, ids, colors, asset paths, audio embeds). No sentence
composition anywhere.
"""

import json
from pathlib import Path

PROJ = Path(__file__).resolve().parent


# ── Audio embed (structural wiring only) ─────────────────────────────

def audio(src, label):
    return (
        f'<p style="font-size:35px;font-weight:700;color:#fff;margin:20px 0 4px 0">{label}</p>'
        f'<audio controls preload="none" src="{src}" '
        f'style="width:70%;max-width:640px;margin:6px auto;display:block"></audio>'
    )


def video(src, label, captions=None, event=None):
    """Audio wrapped in a <video> element (native captions) + JS caption overlay.

    The <video> is sized to its controls only (no wasted black area above).
    captions-plugin.js reads the WebVTT track and renders large high-contrast
    text BELOW the player. `default` on the track lets the plugin activate cues.
    """
    track = (f'<track kind="captions" src="{captions}" srclang="en" default>'
             if captions else "")
    return (
        f'<p style="font-size:35px;font-weight:700;color:#fff;margin:20px 0 4px 0">{label}</p>'
        f'<div class="captions-wrap">'
        f'<video class="caption-video" controls preload="metadata" '
        f'style="width:70%;max-width:640px;margin:0 auto;display:block;height:34px">'
        f'<source src="{src}" type="audio/mpeg">{track}</video>'
        f'<div class="caption-overlay" aria-live="polite"></div>'
        f'</div>'
    )


def youtube_embed(video_id, label):
    """Embed an uploaded YouTube video (native auto-CC + room-readable player).

    Uses the youtube-nocookie host. CC is toggled via YouTube's own captions
    button — auto-generated for the uploaded tape. `enablejsapi=1` lets the
    deck postMessage a pauseVideo command when the slide is left.
    """
    return (
        f'<p style="font-size:35px;font-weight:700;color:#fff;margin:20px 0 4px 0">{label}</p>'
        f'<div style="width:80%;max-width:760px;margin:10px auto 0;aspect-ratio:16/9">'
        f'<iframe src="https://www.youtube-nocookie.com/embed/{video_id}?enablejsapi=1" '
        f'title="YouTube player" style="width:100%;height:100%;border:0;border-radius:8px" '
        f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
        f'allowfullscreen></iframe>'
        f'</div>'
    )


# ── Dictation questions (verbatim, 2 per chunk) ──────────────────────

DICT = {
    1: [
        "What is the key difference between trading with a country and colonising it?",
        "How did the British justify colonisation?",
    ],
    2: [
        "Why was Britain spending so much silver on Chinese tea, silk, and porcelain, and how did the opium trade fix this problem?",
        "What excuse did Britain use to start the First Opium War after Lin Zexu destroyed their opium?",
    ],
    3: [
        "How did the opium trade affect ordinary Chinese families?",
        "What does extraterritoriality mean, and why did it make the Chinese angry?",
    ],
    4: [
        "How did King Mongkut's approach to the British differ from the Chinese emperor's approach?",
        "What strategy did King Chulalongkorn use to keep Thailand independent while giving up forty percent of its territory?",
    ],
}


# ── Answers by interview chunk ───────────────────────────────────────

ANSWERS = {
    1: [
        ("What is the key difference between trading with a country and colonising it?",
         "Trading means voluntary exchange. Colonisation means taking control — making laws, collecting taxes, and using the land and people."),
        ("How did the British justify colonisation?",
         "They said they were bringing civilisation, education, and order. But really they were taking resources and power."),
    ],
    2: [
        ("Why was Britain spending so much silver on Chinese tea, silk, and porcelain, and how did the opium trade fix this problem?",
         "Britain bought tea, silk, and porcelain and had to pay in silver, which drained their economy. Growing opium in India and selling it to China reversed the silver flow."),
        ("What excuse did Britain use to start the First Opium War after Lin Zexu destroyed their opium?",
         "Britain said Lin Zexu destroying their opium was an attack on free trade — that was the excuse for war."),
    ],
    3: [
        ("How did the opium trade affect ordinary Chinese families?",
         "Millions became addicted. Fathers could not work. Families lost everything. The government could not stop it."),
        ("What does extraterritoriality mean, and why did it make the Chinese angry?",
         "British people in China were judged by British courts, not Chinese law. So they could break the law and walk away — China lost control of its own land."),
    ],
    4: [
        ("How did King Mongkut's approach to the British differ from the Chinese emperor's approach?",
         "The Chinese emperor fought back and was defeated. King Mongkut welcomed the British envoy, spoke English, showed his library of Western books, and negotiated."),
        ("What strategy did King Chulalongkorn use to keep Thailand independent while giving up forty percent of its territory?",
         "He gave away far-off border lands he barely controlled — to France and Britain — to protect the heartland. A sacrifice, not a defeat."),
    ],
}


# ── Helpers ───────────────────────────────────────────────────────────

def dict_questions_html(qs):
    return "".join(
        f'<p style="font-size:35px;line-height:1.5;margin:10px 0;text-align:left">{q}</p>'
        for q in qs
    )


def answers_table(pairs):
    rows = []
    for q, a in pairs:
        rows.append(
            f'<tr><td style="padding:8px 12px 8px 0;border-bottom:1px solid #444;'
            f'font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top;width:100px">Question</td>'
            f'<td style="padding:8px 0;border-bottom:1px solid #444;font-size:34px;line-height:1.4">{q}</td></tr>'
        )
        rows.append(
            f'<tr><td style="padding:8px 12px 8px 0;border-bottom:1px solid #444;'
            f'font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top">Answer</td>'
            f'<td style="padding:8px 0;border-bottom:1px solid #444;font-size:34px;line-height:1.4">{a}</td></tr>'
        )
    return '<table style="width:100%;border-collapse:collapse">' + "".join(rows) + "</table>"


# ── Slides ───────────────────────────────────────────────────────────

slides = []

# 1. splash
slides.append({"layout": "image", "id": "splash", "step": 1,
               "image_url": "assets/splash.jpg"})

# 2. title
slides.append({
    "layout": "content", "id": "title", "step": 1,
    "background_image": "assets/splash.jpg", "logo": "assets/logo.png",
    "shield": True,
    "title": "When Britain addicted China to hard drugs.",
    "body": "Let's listen to this amazing story.",
    "notes": "Show the opium-era image. Ask: What do you see? What might this be about?",
})

# 3. importance
slides.append({
    "layout": "content", "id": "importance", "step": 1,
    "background_color": "#1a1a2e",
    "title": "Why is this lesson important?",
    "body": "<ul><li>Colonisation shaped the world — including Thailand.</li>"
            "<li>The opium trade is a controversial chapter of history.</li>"
            "<li>Thailand is the only Southeast Asian country never colonised.</li></ul>",
})

# 4. open dictation (red)
slides.append({
    "layout": "content", "id": "open-dictation", "step": 1,
    "background_color": "#c0392b",
    "title": "Listen and write the questions",
    "body": "<p style=\"font-size:35px;line-height:1.5;margin:10px 0\">"
            "You will hear <strong>eight questions</strong>.<br>"
            "Write each question. You will hear each one <strong>twice</strong>.</p>"
            + audio("assets/questions.mp3", "Dictation tape"),
    "notes": "Play the dictation tape. Students write the 8 questions. Play twice.",
})

# 5-8. dictation check
for c in [1, 2, 3, 4]:
    slides.append({
        "layout": "content", "id": f"dict-check-{c}", "step": 1,
        "background_color": "#1a1a2e",
        "title": f"Check your dictation — Part {c}",
        "body": dict_questions_html(DICT[c]),
        "notes": "Read the two questions aloud. Students tick or correct what they wrote.",
    })

# 9. intro interview (red)
slides.append({
    "layout": "content", "id": "intro-interview", "step": 1,
    "background_color": "#c0392b",
    "title": "Now listen to the podcast",
    "body": "<p style=\"font-size:35px;line-height:1.5;margin:10px 0\">"
            "A history podcast: <strong>It's Academic</strong>.<br>"
            "Host Jack Smith talks to teen researcher Ebony Mills.<br>"
            "There are <strong>four parts</strong>.<br>"
            "Listen to each part <strong>twice</strong>. Then answer the questions.</p>",
    "notes": "Introduce the podcast format: Jack Smith (Stephen Colbert) + Ebony Mills (teen researcher).",
})

# 10-13. tape slides — YouTube embed where uploaded, local video fallback otherwise.
YT_IDS = {1: "PAC65Ewnrdk", 2: "0yCF4E9kgj0", 3: "uSbfURZb7U8", 4: "R2V0w2Ob5PA"}
for i in [1, 2, 3, 4]:
    instr = ("<p style=\"font-size:35px;color:#f0f0f0;margin:0 0 12px 0\">"
             "You will hear each tape 2 times. "
             "Captions off first time; on second time.</p>")
    if i in YT_IDS:
        body = instr + youtube_embed(YT_IDS[i], f"Listen to Part {i}")
        notes = (f"Play Part {i} (YouTube). First pass without subtitles, "
                 f"second pass with CC on (YouTube auto-captions).")
    else:
        body = instr + video(f"assets/tape{i}.mp3", f"Listen to Part {i}",
                     captions=f"assets/tape{i}.vtt")
        notes = (f"Play Part {i} twice (local player). First pass without "
                 f"subtitles, second pass with subtitles on.")
    slides.append({
        "layout": "content", "id": f"tape-{i}", "step": 1,
        "background_color": "#1a1a2e",
        "title": f"Podcast — Part {i}",
        "body": body,
        "notes": notes,
    })

# 14-17. answers by chunk (green)
for c in [1, 2, 3, 4]:
    slides.append({
        "layout": "content", "id": f"answer-{c}", "step": 1,
        "background_color": "#052e0d",
        "title": f"Answers — Part {c}",
        "body": answers_table(ANSWERS[c]),
        "notes": "Read each question, ask students, then reveal the answer.",
    })

# 18. model card (full-screen 5-step graphic, no side text)
slides.append({
    "layout": "image", "id": "model-card", "step": 1,
    "image_url": "assets/card-model.png",
    "background_color": "#1a1a2e",
    "notes": "Walk through the 5-step structure on the card. Model one short example with a student.",
})

# 18b. Strategy — the resolution (technique)
slides.append({
    "layout": "content", "id": "strategy-compromise", "step": 1,
    "background_color": "#1a1a2e",
    "title": "Strategy: Close the discussion",
    "body": "<table style=\"width:100%;border-collapse:collapse\"><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #555;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Do</td><td style=\"padding:8px 0;border-bottom:1px solid #555\">End the talk by stating the compromise you both accept.</td></tr><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #555;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Why</td><td style=\"padding:8px 0;border-bottom:1px solid #555\">A clear resolution shows you understood and agreed.</td></tr><tr><td style=\"padding:8px 12px 8px 0;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">How</td><td style=\"padding:8px 0\">Summarise the middle point. Then say: \"So, can we compromise and say ...?\"</td></tr></table>",
    "notes": "Teach the ENDING. Summarise the middle point, then state the resolution both partners accept. One closing sentence each.",
})

# 18c. Strategy demo — Card 1 worked example (B2)
slides.append({
    "layout": "content", "id": "strategy-compromise-demo", "step": 1,
    "background_color": "#116466",
    "title": "Card 1 — the resolution",
    "body": "<p style=\"font-size:35px;line-height:1.5;margin:0 0 10px 0;color:#fff\"><strong>Card 1:</strong> Is it ever OK to break a rule to do the right thing?</p>"
            "<table style=\"width:100%;border-collapse:collapse\"><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #444;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Partner A</td><td style=\"padding:8px 0;border-bottom:1px solid #444\">\"Breaking a rule is always wrong.\"</td></tr><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #444;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Partner B</td><td style=\"padding:8px 0;border-bottom:1px solid #444\">\"I see your point, but sometimes the rule is unfair.\"</td></tr><tr><td style=\"padding:8px 12px 8px 0;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Resolution</td><td style=\"padding:8px 0\">\"So, can we compromise and say we decide by the rule and the reason?\"</td></tr></table>",
    "notes": "Model the END of the discussion — the resolution. Partner A vs B, then both state the final compromise. Students repeat the 'So, can we compromise and say...?' closing pattern.",
})

# 18d. Resolution language (B2)
slides.append({
    "layout": "content", "id": "strategy-compromise-lang", "step": 1,
    "background_color": "#1a1a2e",
    "title": "Resolution — closing the discussion",
    "body": "<p style=\"font-size:35px;line-height:1.5;margin:0 0 10px 0;text-align:left\"><strong>State the agreement</strong>: \"So, can we compromise and say ... ?\"</p>"
            "<p style=\"font-size:35px;line-height:1.5;margin:0 0 10px 0;text-align:left\"><strong>Or</strong>: \"Could we agree that ... ?\" \"Maybe we can both ...\"</p>"
            "<p style=\"font-size:35px;line-height:1.5;margin:0 0 10px 0;text-align:left\"><strong>Confirm</strong>: \"So we both think ..., right?\"</p>"
            "<p style=\"font-size:35px;line-height:1.5;margin:0;text-align:left\"><strong>Close</strong>: \"Great, we agree on that.\"</p>",
    "notes": "Step 5 endings — these close the discussion. One resolution statement that both partners say together.",
})

# 19. speed dating — Set A (structured)
slides.append({
    "layout": "content", "id": "speed-cp", "step": 1,
    "background_color": "#116466",
    "title": "Speed dating — Card Set A",
    "body": "<img src=\"assets/cards-cp-1.png\" alt=\"Set A structured card\" "
            "style=\"width:38%;max-height:330px;object-fit:contain;margin:6px auto;display:block;border-radius:6px\">"
            "<p style=\"font-size:35px;line-height:1.45;margin:12px 0 6px 0\">"
            "Pair up. One card each. Discuss for <strong>2 minutes</strong>.</p>"
            "<p style=\"font-size:35px;line-height:1.45;margin:0\">"
            "Use the structure and the language on the card. Then move to the next partner.</p>",
    "notes": "Set A = structured cards with language support. 2-minute rounds. Rotate partners.",
})

# 20. speed dating — Set B (bare)
slides.append({
    "layout": "content", "id": "speed-fp", "step": 1,
    "background_color": "#116466",
    "title": "Speed dating — Card Set B",
    "body": "<img src=\"assets/cards-fp.png\" alt=\"Set B bare card\" "
            "style=\"width:38%;max-height:330px;object-fit:contain;margin:6px auto;display:block;border-radius:6px\">"
            "<p style=\"font-size:35px;line-height:1.45;margin:12px 0 6px 0\">"
            "Now no language help. Talk for <strong>2 minutes</strong>.</p>"
            "<p style=\"font-size:35px;line-height:1.45;margin:0\">"
            "Use your own ideas. Then move to the next partner.</p>",
    "notes": "Set B = bare cards, no language support. Students must use the structure on their own.",
})

data = {
    "title": "The Opium Wars and the Country That Got Away",
    "author": "Ed Rush",
    "theme": "black",
    "transition": "slide",
    "slides": slides,
}

out = PROJ / "data.json"
out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {out} — {len(slides)} slides")
