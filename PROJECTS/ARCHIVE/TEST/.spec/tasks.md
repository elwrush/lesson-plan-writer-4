## Tasks

- [x] PT001 **Research reference materials** — read `esl-voice.md`, `best-practices.md`, and `slideshow_lib-quickref.md` from the slideshow-renderer skill to understand voice, design rules, and available functions
- [x] PT002 **Write data.json** — 10 slides covering Present Perfect Simple with stage, title, body, notes for each
- [x] PT003 **Write template.jinja2** — uses slideshow_lib functions: `slide_bg` (stage colors), `slide_transition`, `fragment` filter (for reveal steps), `auto_animate_pair` (for affirmative→negative→question transformation), `notes` filter
- [x] PT004 **Render slides** — run `python ~/.kilo/skills/slideshow-renderer/scripts/render.py template.jinja2 data.json --output slides/index.html`
- [x] PT005 **Verify output** — open `slides/index.html` in browser, confirm CDN loads, all 10 slides render, auto-animate works, fragments work, speaker notes present
- [x] PT006 **Deploy via git-pages** — run `/git-pages TEST PROJECTS/TEST/slides` and confirm live URL loads
