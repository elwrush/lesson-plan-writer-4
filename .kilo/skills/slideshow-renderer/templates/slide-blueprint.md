# Slide blueprint — pure JSON→Jinja2→reveal.js — {lesson title}

1. splash — image (splash.jpg only)
2. title — content (logo + shield + background_image)
3. importance — content (navy, <ul> of real-world outcomes)
4. recall-xxx — content (navy, timed pair discussion with data-timer-autostart)
5. transition-vocab — content (red, "Let's check your word knowledge")
6. vocab-xxx — raw (navy, left-aligned table, 3-click reveal: phonemic → box-word → context+clarification)
7. vocab-yyy — raw (navy, same pattern)
...
11. strategy-xxx — content (navy, Do/Why/How HTML table)
12. demo-xxx — auto-animate-pair (navy, table, matching DOM: &nbsp; spans, uniform borders)
...
18. answer-xxx — content (green, HTML table: Question / Answer / Explanation / Transcript)

## Checklist

- [ ] Splash: image layout, image_url only, no title/body
- [ ] Title: logo + shield + background_image (all three)
- [ ] Importance: immediately after title, dark navy, <ul>
- [ ] Vocab preceded by red transition: "Let's check your word knowledge"
- [ ] Vocab: raw layout, left-aligned table, 3 fragment rows (phonemic→box-word→context), no syllable dots
- [ ] Vocab: context sentence has clarifying second clause ("...I was so interested...")
- [ ] Each strategy followed by a demo (auto-animate-pair table, not real transcript content)
- [ ] Strategy demos: identical DOM between steps, uniform border-bottom on every <td>, &nbsp; in empty spans
- [ ] Strategy demos: use <span> not <strong> for invisible placeholders (no default bold)
- [ ] Answer slides: one question per slide, HTML table (Question/Answer/Explanation/Transcript)
- [ ] Answer slides: Answer row text in yellow bold (#ffdd00), Transcript in italic
- [ ] Timed slides: data-timer in post-process.py (use data-id="slide-{id}-1" from resolver)
- [ ] Timer auto-start: data-timer-autostart="true" for recall/warm-up slides
- [ ] Headers left-aligned: content and auto-animate-pair slides prepend `<style>h2{text-align:left!important;margin-left:0!important;margin-right:0!important}</style>` to body
- [ ] Max 25 body words per content slide, 8-12 words per sentence, one idea per sentence
- [ ] Page and task numbers referenced on every task slide (e.g. "Page 155, Task 1")
- [ ] Color stages: navy (content), red (transitions/tasks), green (answers), purple (freer practice)
- [ ] Body content is raw HTML passed verbatim through Jinja2 to reveal.js
