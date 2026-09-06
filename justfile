# justfile — LESSON-PLAN-WRITER-4
#
# Opinions task runner for the data-only repo. Keeps the multi-command
# workflows the AI runs every time in one place, so the agent never has to
# re-derive paths or command order.
#
# Usage:
#   just render name="LISTENING M3"   # build -> render -> postprocess -> validate (full loop)
#   just validate name="LISTENING M3" # font validation only
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
