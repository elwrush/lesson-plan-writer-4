#!/usr/bin/env python3
"""
Build data.json for the Nepal flood listening + speaking deck.
Slide TEXT is authored verbatim as literal strings below; helpers only wire
structure (layout, ids, colors, asset paths, audio embeds). No sentence
composition anywhere.
"""

import json
from pathlib import Path

PROJ = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Audio embed (structural wiring only — the label text is a verbatim string)
# ---------------------------------------------------------------------------
def audio(src, label):
    return (
        f'<p style="font-size:35px;font-weight:700;color:#fff;margin:20px 0 4px 0">{label}</p>'
        f'<audio controls preload="none" src="{src}" '
        f'style="width:70%;max-width:640px;margin:6px auto;display:block"></audio>'
    )


def youtube_embed(video_id, label):
    """Embed a YouTube video (native auto-CC on by default + pauseable player).

    enablejsapi=1 allows the deck to postMessage pauseVideo on slidechange.
    cc_load_policy=1 turns captions on by default (YouTube auto-captions).
    """
    return (
        f'<p style="font-size:35px;font-weight:700;color:#fff;margin:20px 0 4px 0">{label}</p>'
        f'<div style="width:80%;max-width:760px;margin:10px auto 0;aspect-ratio:16/9">'
        f'<iframe src="https://www.youtube-nocookie.com/embed/{video_id}?enablejsapi=1&cc_load_policy=1" '
        f'title="YouTube player" style="width:100%;height:100%;border:0;border-radius:8px" '
        f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
        f'allowfullscreen></iframe>'
        f'</div>'
    )


# ── Dictation questions (verbatim) by chunk ──────────────────────────
DICT = {
    1: [
        "Why does Emma say the flood was not normal?",
        "Why was the loud noise so surprising?",
    ],
    2: [
        "Why did many people first think it was an earthquake?",
        "Why can't scientists warn people before a glacier breaks?",
    ],
    3: [
        "Give two examples of damage to buildings and roads.",
        "How many people were affected, and how many children lost their classrooms?",
    ],
    4: [
        "Why does Emma say the danger is not over?",
        "Why is this a climate story, not only a Nepal story?",
    ],
}

# ---------------------------------------------------------------------------
# Answers by interview chunk (Question -> Answer, B1, verbatim)
# ---------------------------------------------------------------------------
ANSWERS = {
    1: [
        ("Why does Emma say the flood was not normal?",
         "A normal flood rises slowly. This flood was a wall of water, mud, rocks and broken ice, and it moved very fast."),
        ("Why was the loud noise so surprising?",
         "It sounded like thunder, but the sky was clear and blue, with no clouds."),
    ],
    2: [
        ("Why did many people first think it was an earthquake?",
         "The US Geological Survey recorded a small tremor, about 4.4. So people thought the earthquake had caused a landslide."),
        ("Why can't scientists warn people before a glacier breaks?",
         "The Himalayas are huge and remote, and the weather was calm that day. There are thousands of glaciers, so scientists cannot say which one will break, or when."),
    ],
    3: [
        ("Give two examples of damage to buildings and roads.",
         "It destroyed homes, roads and bridges. It also blocked the tunnels of hydroelectric power stations."),
        ("How many people were affected, and how many children lost their classrooms?",
         "About 65,000 people were affected. Around 10,000 children lost their classrooms."),
    ],
    4: [
        ("Why does Emma say the danger is not over?",
         "A barrier lake has formed behind rocks and debris. Water is building up, and if it breaks, there could be a second flood."),
        ("Why is this a climate story, not only a Nepal story?",
         "The warming planet makes flooding worse across Asia. Thailand is also at risk, and countries like Nepal cause little of the problem but feel it first."),
    ],
}


def dict_questions_html(qs):
    lis = "".join(f'<p style="font-size:35px;line-height:1.5;margin:10px 0;text-align:left">{q}</p>' for q in qs)
    return lis


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


# ---------------------------------------------------------------------------
# Slides (verbatim authored text)
# ---------------------------------------------------------------------------
slides = []

# 1. splash — image only
slides.append({"layout": "image", "id": "splash", "step": 1,
               "image_url": "assets/splash.jpg"})

# 2. title
slides.append({
    "layout": "content", "id": "title", "step": 1,
    "background_image": "assets/splash.jpg", "logo": "assets/logo.png",
    "shield": True,
    "title": "The flood at the China-Nepal border",
    "body": "What happened? Why? What can we do?",
    "notes": "Point at the flood image. Ask: Where is this? What do you see?",
})

# 3. importance
slides.append({
    "layout": "content", "id": "importance", "step": 1,
    "background_color": "#1a1a2e",
    "title": "Why is this lesson important?",
    "body": "<ul><li>This flood shows how a small event can become a disaster.</li>"
            "<li>Floods are a real risk across Asia, including Thailand.</li>"
            "<li>You will practise talking about climate change in English.</li></ul>",
})

# 3b. real footage — the border crossing destroyed
slides.append({
    "layout": "content", "id": "footage", "step": 1,
    "background_color": "#1a1a2e",
    "title": "The border crossing, destroyed",
    "body": "<p style=\"font-size:35px;color:#f0f0f0;margin:0 0 12px 0\">"
            "Watch the real footage. This is the town you will hear about.</p>"
            + youtube_embed("FFYBmDYQqoA", "The flood at the border crossing"),
    "notes": "Play the short clip. Ask: What can you see? This is Gyirong, the border crossing on the China-Nepal border — destroyed by the flood.",
})

# 4. open dictation (red)
slides.append({
    "layout": "content", "id": "open-dictation", "step": 1,
    "background_color": "#c0392b",
    "title": "Listen and write the questions",
    "body": "<p style=\"font-size:35px;line-height:1.5;margin:10px 0\">"
            "You will hear <strong>eight questions</strong>.<br>"
            "Write each question. You will hear each one <strong>twice</strong>.</p>"
            + audio("assets/questions.mp3?v=2", "Dictation tape"),
    "notes": "Play the dictation tape. Students write the 8 questions as they hear them. Play twice.",
})

# 5-8. dictation check, one chunk per slide (2 questions, no //)
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
            "A podcast about the flood.<br>"
            "There are <strong>four parts</strong>.<br>"
            "Listen to each part. Then answer its questions.<br>"
            "You will play each part again yourself.</p>",
    "notes": "Introduce the podcast: Lucy Milligan (journalist) interviews Emma McKinley (aid worker). Each part is played once; the teacher replays it as needed, and captions are on by default.",
})

# 10-17. tape + answers INTERLEAVED: tape-1 -> answer-1 -> tape-2 -> answer-2 ...
# Each part is a SINGLE play (no 'listen again' inside). The teacher controls any
# second listen. Captions are on by default (cc_load_policy=1) so students can
# read along after the first blind listen.
YT_IDS = {1: "asFSmtUjhLk", 2: "ofuhUv7ySZs", 3: "oqFaFHTFevs", 4: "kk5xW5HuN0E"}
for i in [1, 2, 3, 4]:
    instr = ("<p style=\"font-size:35px;color:#f0f0f0;margin:0 0 12px 0\">"
             "Play this part once. Captions are on.<br>"
             "Then answer the two questions.</p>")
    body = instr + youtube_embed(YT_IDS[i], f"Listen to Part {i}")
    notes = (f"Play Part {i} (YouTube, single play). Captions are ON by default. "
             f"First pass: listen for gist with captions hidden if desired; "
             f"teacher replays as needed.")
    slides.append({
        "layout": "content", "id": f"tape-{i}", "step": 1,
        "background_color": "#1a1a2e",
        "title": f"Podcast — Part {i}",
        "body": body,
        "notes": notes,
    })
    # answers immediately follow this part
    slides.append({
        "layout": "content", "id": f"answer-{i}", "step": 1,
        "background_color": "#052e0d",
        "title": f"Answers — Part {i}",
        "body": answers_table(ANSWERS[i]),
        "notes": "Read each question, ask students, then reveal the answer.",
    })

# 18. model card (two-column)
slides.append({
    "layout": "two-column", "id": "model-card", "step": 1,
    "background_color": "#1a1a2e",
    "title": "A speaking card",
    "body": "<img src=\"assets/card-model.png\" alt=\"Model speaking card\" "
            "style=\"width:100%;height:100%;object-fit:contain;border-radius:8px\">"
            "|||"
            "<p style=\"font-size:35px;line-height:1.55;margin:0 0 14px 0\">"
            "Work with a partner. Use the card structure.</p>"
            "<p style=\"font-size:35px;line-height:1.55;margin:0 0 8px 0\">"
            "<strong>Open</strong> — start the talk.</p>"
            "<p style=\"font-size:35px;line-height:1.55;margin:0 0 8px 0\">"
            "<strong>Opinion</strong> — say what you think.</p>"
            "<p style=\"font-size:35px;line-height:1.55;margin:0 0 8px 0\">"
            "<strong>Reason</strong> — give a reason.</p>"
            "<p style=\"font-size:35px;line-height:1.55;margin:0 0 8px 0\">"
            "<strong>Agree or disagree</strong> — reply to your partner.</p>"
            "<p style=\"font-size:35px;line-height:1.55;margin:0\">"
            "<strong>Agreement</strong> — find a compromise.</p>",
    "notes": "Walk through the 5-step structure on the card. Model one short example with a student.",
})

# 19. strategy — close the discussion (technique, B1)
slides.append({
    "layout": "content", "id": "strategy-compromise", "step": 1,
    "background_color": "#1a1a2e",
    "title": "Strategy: Close the discussion",
    "body": "<table style=\"width:100%;border-collapse:collapse\"><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #555;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Do</td><td style=\"padding:8px 0;border-bottom:1px solid #555\">End the talk by saying the compromise you both accept.</td></tr><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #555;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Why</td><td style=\"padding:8px 0;border-bottom:1px solid #555\">A clear resolution shows you understood and agreed.</td></tr><tr><td style=\"padding:8px 12px 8px 0;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">How</td><td style=\"padding:8px 0\">Say the middle point. Then say: \"So, can we compromise and say ...?\"</td></tr></table>",
    "notes": "Teach the ENDING. Summarise the middle point, then state the resolution both partners accept. One closing sentence each.",
})

# 19b. strategy demo — Card 1 resolution (B1)
slides.append({
    "layout": "content", "id": "strategy-compromise-demo", "step": 1,
    "background_color": "#116466",
    "title": "Card 1 — the resolution",
    "body": "<p style=\"font-size:35px;line-height:1.5;margin:0 0 10px 0;color:#fff\"><strong>Card 1:</strong> Is climate change mainly caused by people?</p>"
            "<table style=\"width:100%;border-collapse:collapse\"><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #444;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Partner A</td><td style=\"padding:8px 0;border-bottom:1px solid #444\">\"I think people cause climate change.\"</td></tr><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #444;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Partner B</td><td style=\"padding:8px 0;border-bottom:1px solid #444\">\"I see your point, but nature also changes the weather.\"</td></tr><tr><td style=\"padding:8px 12px 8px 0;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Resolution</td><td style=\"padding:8px 0\">\"So, can we compromise and say people and nature both play a part?\"</td></tr></table>",
    "notes": "Model the END of the discussion — the resolution. Partner A vs B, then both state the final compromise. Students repeat the 'So, can we compromise and say...?' pattern.",
})

# 19c. resolution language (B1)
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

# 20. speed dating — controlled practice (Set A cards)
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

# 20. speed dating — freer practice (Set B cards)
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
    "title": "The Flood at the China-Nepal Border",
    "author": "Ed Rush",
    "theme": "black",
    "transition": "slide",
    "slides": slides,
}

out = PROJ / "data.json"
out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {out} — {len(slides)} slides")
