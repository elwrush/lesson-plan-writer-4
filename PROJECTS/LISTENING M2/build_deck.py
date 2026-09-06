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
    """Embed a YouTube video (native auto-CC + pauseable player).

    enablejsapi=1 allows the deck to postMessage pauseVideo on slidechange.
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


# ── Dictation questions (verbatim) by chunk ──────────────────────────
DICT = {
    1: [
        "Emma says the flood was not a normal flood. What was it like, and why was it so dangerous?",
        "Why was the loud noise so surprising to the people in Nuwakot?",
    ],
    2: [
        "Why did so many people first believe that there had been an earthquake?",
        "Why is it so hard for scientists to warn people before a glacier collapses?",
    ],
    3: [
        "Give two examples of the damage that the flood caused to buildings and infrastructure.",
        "How many people were affected in total, and around how many children lost their classrooms?",
    ],
    4: [
        "Emma says the danger is not over. Why?",
        "Why does Emma think that this is a climate story, and not only a Nepal story?",
    ],
}

# ---------------------------------------------------------------------------
# Answers by interview chunk (Question -> Answer, B1, verbatim)
# ---------------------------------------------------------------------------
ANSWERS = {
    1: [
        ("What was the flood like, and why was it so dangerous?",
         "It was a wall of water, mud, rocks and broken ice. It moved incredibly fast, so people had no time to run."),
        ("Why was the loud noise so surprising?",
         "It sounded like thunder, but the sky was clear and blue, with no clouds."),
    ],
    2: [
        ("Why did many people first think it was an earthquake?",
         "The US Geological Survey recorded a small tremor, about 4.4. So people thought the earthquake had caused a landslide."),
        ("Why is it so hard to warn people before a glacier collapses?",
         "The Himalayas are huge and remote, and the weather was calm that day. There are thousands of glaciers, so scientists cannot say which one will break, or when."),
    ],
    3: [
        ("Give two examples of damage to buildings and infrastructure.",
         "It destroyed homes, roads and bridges. It also blocked the tunnels of hydroelectric power stations."),
        ("How many people were affected? How many children lost classrooms?",
         "About 65,000 people were affected. Around 10,000 children lost their classrooms."),
    ],
    4: [
        ("Why is the danger not over?",
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

# 4. open dictation (red)
slides.append({
    "layout": "content", "id": "open-dictation", "step": 1,
    "background_color": "#c0392b",
    "title": "Listen and write the questions",
    "body": "<p style=\"font-size:35px;line-height:1.5;margin:10px 0\">"
            "You will hear <strong>eight questions</strong>.<br>"
            "Write each question. You will hear each one <strong>twice</strong>.</p>"
            + audio("assets/questions.mp3", "Dictation tape"),
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
            "Listen to each part <strong>twice</strong>. Then answer the questions.</p>",
    "notes": "Introduce the podcast: Lucy Milligan (journalist) interviews Emma McKinley (aid worker).",
})

# 10-13. tape slides — YouTube embed where uploaded, local audio fallback otherwise.
YT_IDS = {1: "lPJsRuss8ds", 2: "q56S8jMamw8", 3: "0nTpP8rPUgM", 4: "cpmaIOXekbQ"}
for i in [1, 2, 3, 4]:
    instr = ("<p style=\"font-size:35px;color:#f0f0f0;margin:0 0 12px 0\">"
             "You will hear each tape 2 times. "
             "Captions off first time; on second time.</p>")
    if i in YT_IDS:
        body = instr + youtube_embed(YT_IDS[i], f"Listen to Part {i}")
        notes = (f"Play Part {i} (YouTube). First pass without subtitles, "
                 f"second pass with CC on (YouTube auto-captions).")
    else:
        body = instr + audio(f"assets/tape{i}.mp3", "Listen to Part " + str(i))
        notes = f"Play Part {i} twice. Students answer the questions for this part."
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
