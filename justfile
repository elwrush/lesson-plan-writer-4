# justfile — LESSON-PLAN-WRITER-4
#
# Opinions task runner for the data-only repo. Keeps the multi-command
# workflows the AI runs every time in one place, so the agent never has to
# re-derive paths or command order.
#
# Usage:
#   just render name="LISTENING M3"   # build -> render -> postprocess -> validate (full loop)
#   just validate name="LISTENING M3" # font validation only
#   just indread-render name="READING M2" # independent reading render+combine (post-gate)
#   just reading-check name="READING M3"  # word-band + gloss-integrity check (pre-flight)
#   just test                         # pytest
#   just serve                        # start background HTTP server on :8080 (idempotent)
#   just help                         # list recipes
#
# NOTE on the `name` arg: project dirs contain a SPACE (e.g. "LISTENING M3").
# Recipe args are passed positionally / as a VALUE, not as key=value on the
# CLI. Quote the whole value:   just render "LISTENING M3"
# (The default is "LISTENING M3", so `just render` works with no arg.)

# Global paths — these live OUTSIDE the repo (global skills dir), so they are
# stable across projects. Quote them: an unquoted /foo//bar/ path trips just's
# `//` comment operator in 1.21. Reference {{RENDERER}} inline in recipes
# (just does NOT recursively expand a var that itself contains {{...}}).
RENDERER := "/home/elwru/.agents/skills/slideshow-renderer"
INDR := "/home/elwru/.agents/skills/independent-reading-text-generator"

# Name of a project dir (defaults to the M3 listening lesson).
name := "LISTENING M3"

# ── Full dev loop ────────────────────────────────────────────────────────────
# Build data.json, render index.html, inject timers/plugins, validate fonts.
# Requires the project to have build_deck.py (LISTENING M2 / M3 do).
render	name=name:
	@echo "==[ build_deck ]=="
	@python3 "PROJECTS/{{name}}/build_deck.py"
	@echo "==[ render ]=="
	@python3 "{{RENDERER}}/scripts/render.py" --data "PROJECTS/{{name}}/data.json" --output "PROJECTS/{{name}}/slides/index.html"
	@echo "==[ post-process ]=="
	@python3 "PROJECTS/{{name}}/post-process.py"
	@echo "==[ validate fonts ]=="
	@python3 "{{RENDERER}}/scripts/validate_slide_fonts.py" "PROJECTS/{{name}}/data.json"
	@echo "==[ done ]=="

# ── Font validation only ─────────────────────────────────────────────────────
validate	name=name:
	@python3 "{{RENDERER}}/scripts/validate_slide_fonts.py" "PROJECTS/{{name}}/data.json"

# ── Independent reading render + combine (POST-GATE) ────────────────────────
# Terminal production step for the independent-reading generator. The
# simplify → Kimi → human gates are INTERACTIVE and are NOT wrapped here;
# this runs only AFTER the human approves (human_approved=True in the
# payload). Reads the project's SCRIPTS/reading.json envelope, renders each
# level to PDF, merges them (B1 first, then B2) into one combined PDF, and
# verifies each.
# Independent-reading render+combine (POST-GATE): renders the project's SCRIPTS/reading.json levels to PDF then merges B1+B2 into one PDF. Only after human approval.
indread-render	name=name:
	@echo "==[ independent reading render+combine: {{name}} ]=="
	@python3 "INDEPENDENT-READING/PROJECTS/{{name}}/SCRIPTS/produce.py"
	@echo "==[ done ]=="

# ── Reading envelope check (word-band + gloss integrity) ─────────────────────
# Runs the project's produce.py --check: sanitises + reports the body word
# count against [target, cap] AND verifies every gloss word appears verbatim
# in the body. A missing gloss word is a data bug (silently dropped by
# sanitise and, pre-fix, the cause of the off-by-one gloss-numbering error);
# --check surfaces it and the render path hard-fails on it.
#   just reading-check "READING M3"
reading-check	name="READING M3":
	@echo "==[ reading check: {{name}} ]=="
	@python3 "INDEPENDENT-READING/PROJECTS/{{name}}/SCRIPTS/produce.py" --check
	@echo "==[ done ]=="

# ── Lesson plan render + verify ──────────────────────────────────────────────
# Renders PROJECTS/{name}/lesson-plan-envelope.json via the write-lesson-plan
# skill to the repo-root PDF/ (the skill's mandated output location), then runs
# scripts/verify_lesson_plan.py: A4 page-size, fonts embedded, content markers
# (topic/class/teacher/main-aim), NO Transcript section (reading lesson), and no
# contextual images beyond the two masthead logos. The envelope is hand-authored
# by the agent from the shape + source materials (like reading.json); this wraps
# the deterministic render+verify so the gates always run.
#   just lesson-plan "READING M2"
lesson-plan	name="READING M2":
	@echo "==[ lesson plan render+verify: {{name}} ]=="
	@python3 ~/.agents/skills/write-lesson-plan/scripts/render.py --template lesson-plan --data "PROJECTS/{{name}}/lesson-plan-envelope.json"
	@python3 scripts/verify_lesson_plan.py "PROJECTS/{{name}}/lesson-plan-envelope.json"
	@echo "==[ done ]=="

# ── gh-pages slideshow deploy (old-origin; isolated worktree; MD5-verified) ──
# Deploys PROJECTS/{name}/slides to gh-pages on old-origin (the canonical slides
# host; falls back to origin). Uses the shared scripts/deploy_pages.py, which
# builds the landing page from the git tree (NOT os.listdir on a sparse clone —
# that bug silently dropped presentations) and verifies the push back by MD5.
# Performs a REAL push to the live gh-pages site — only run when you intend to
# publish. The /git-pages opencode command dispatches to the same script.
#   just git-pages "READING M2"
git-pages	name="READING M2":
	@python3 scripts/deploy_pages.py "{{name}}" "PROJECTS/{{name}}/slides"

# ── Test suite ───────────────────────────────────────────────────────────────
test:
	@python3 -m pytest tests/ -v

# ── HTTP server :8080 (idempotent — won't start a 2nd if already listening) ──
serve:
	@if python3 -c "import socket; s=socket.socket(); s.settimeout(0.5); s.connect(('127.0.0.1',8080)); s.close()" 2>/dev/null; then \
		echo "server already running on :8080"; \
	else \
		echo "starting http.server :8080 (background)"; \
		nohup python3 -m http.server 8080 > /tmp/opencode/just-http.log 2>&1 & \
		echo "pid $$!"; \
	fi

# ── Help / list ──────────────────────────────────────────────────────────────
help:
	@just --list
