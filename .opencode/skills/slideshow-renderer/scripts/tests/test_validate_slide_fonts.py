"""
Red/Green tests for validate_slide_fonts.py.

Red phase: confirm violations are detected.
Green phase: confirm clean data passes.
"""

import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_slide_fonts import validate, _is_gray_hex, _scan_text, GRAY_NAMED


# ── Unit: _is_gray_hex ───────────────────────────────────────────────────

class TestIsGrayHex:
    def test_888_is_gray(self):
        assert _is_gray_hex("#888") is True

    def test_ccc_is_gray(self):
        assert _is_gray_hex("#ccc") is True

    def test_fff_is_not_gray(self):
        assert _is_gray_hex("#fff") is False

    def test_000_is_not_gray(self):
        assert _is_gray_hex("#000") is False

    def test_ffdd00_is_not_gray(self):
        assert _is_gray_hex("#ffdd00") is False

    def test_3498db_is_not_gray(self):
        assert _is_gray_hex("#3498db") is False

    def test_aabbcc_is_gray(self):
        assert _is_gray_hex("#aabbcc") is True

    def test_2ecc71_is_not_gray(self):
        assert _is_gray_hex("#2ecc71") is False


# ── Unit: _scan_text ─────────────────────────────────────────────────────

class TestScanText:
    def test_detects_small_font(self):
        v: list[str] = []
        _scan_text('style="font-size:24px"', v, "test")
        assert len(v) == 1
        assert "24px" in v[0]

    def test_28px_is_ok(self):
        v: list[str] = []
        _scan_text('style="font-size:28px"', v, "test")
        assert len(v) == 0

    def test_detects_gray_named(self):
        for name in ("gray", "grey", "lightgray", "darkgray", "silver"):
            v: list[str] = []
            _scan_text(f'color:{name}', v, "test")
            assert len(v) == 1, f"should detect {name}"
            assert name in v[0]

    def test_detects_gray_hex(self):
        v: list[str] = []
        _scan_text('color:#888', v, "test")
        assert len(v) == 1

    def test_white_is_ok(self):
        v: list[str] = []
        _scan_text('color:#fff', v, "test")
        assert len(v) == 0

    def test_yellow_is_ok(self):
        v: list[str] = []
        _scan_text('color:#ffdd00', v, "test")
        assert len(v) == 0


# ── RED phase: confirm violations on bad data ────────────────────────────

class TestRedPhase:
    def test_small_font_violation(self):
        data = {
            "title": "Bad Font",
            "slides": [
                {"layout": "content", "id": "s1", "step": 1,
                 "body": '<p style="font-size:20px">too small</p>'}
            ],
        }
        violations = validate(data)
        assert len(violations) >= 1
        assert any("20px" in v for v in violations)

    def test_gray_font_violation(self):
        data = {
            "title": "Gray Font",
            "slides": [
                {"layout": "content", "id": "s1", "step": 1,
                 "body": '<p style="color:#888">gray text</p>'}
            ],
        }
        violations = validate(data)
        assert len(violations) >= 1
        assert any("#888" in v for v in violations)

    def test_gray_named_violation(self):
        data = {
            "title": "Gray Named",
            "slides": [
                {"layout": "content", "id": "s1", "step": 1,
                 "body": '<p style="color:gray">gray text</p>'}
            ],
        }
        violations = validate(data)
        assert len(violations) >= 1
        assert any("gray" in v for v in violations)

    def test_multiple_violations(self):
        data = {
            "title": "Multiple",
            "slides": [
                {"layout": "content", "id": "s1", "step": 1,
                 "title": '<span style="font-size:14px">tiny</span>',
                 "body": '<p style="color:#aaa">gray body</p>'},
                {"layout": "raw", "id": "s2", "step": 1,
                 "body": '<span style="color:#ccc;font-size:22px">both wrong</span>'},
            ],
        }
        violations = validate(data)
        assert len(violations) >= 3

    def test_fragment_violation(self):
        data = {
            "title": "Fragment",
            "slides": [
                {"layout": "content", "id": "s1", "step": 1,
                 "title": "OK", "fragments": ["<span style=\"color:#bbb\">bad</span>"]}
            ],
        }
        violations = validate(data)
        assert len(violations) >= 1


# ── GREEN phase: confirm clean data passes ───────────────────────────────

class TestGreenPhase:
    def test_minimal_deck(self):
        data = {
            "title": "Clean",
            "slides": [
                {"layout": "content", "id": "s1", "step": 1, "title": "Hello"}
            ],
        }
        assert validate(data) == []

    def test_full_deck_no_gray(self):
        data = {
            "title": "Clean",
            "slides": [
                {"layout": "content", "id": "s1", "step": 1,
                 "title": "Big Title",
                 "body": '<p style="color:#fff;font-size:32px">white text</p>',
                 "fragments": ['<span style="color:#ffdd00;font-size:36px">yellow</span>']},
                {"layout": "raw", "id": "s2", "step": 1,
                 "body": '<p style="color:#3498db;font-size:34px">blue text</p>'},
            ],
        }
        assert validate(data) == []

    def test_28px_boundary(self):
        data = {
            "title": "Boundary",
            "slides": [
                {"layout": "content", "id": "s1", "step": 1,
                 "body": '<p style="font-size:28px">minimum ok</p>'}
            ],
        }
        assert validate(data) == []

    def test_vivid_colors_ok(self):
        data = {
            "title": "Vivid",
            "slides": [
                {"layout": "content", "id": "s1", "step": 1,
                 "body": '<p style="color:#ffdd00">yellow</p><p style="color:#2ecc71">green</p>'}
            ],
        }
        assert validate(data) == []

    def test_empty_deck(self):
        data = {"title": "Empty", "slides": []}
        assert validate(data) == []
