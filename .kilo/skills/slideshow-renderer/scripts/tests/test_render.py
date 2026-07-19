import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

SKILL_DIR = Path.home() / ".kilo" / "skills" / "slideshow-renderer"
LIB_DIR = SKILL_DIR / "lib"
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(LIB_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from render import (
    LayoutType,
    SlideRecord,
    DeckData,
    ResolvedSlide,
    resolve_deck,
    render_deck,
    _find_macros,
)


# ── Fixtures ─────────────────────────────────────────────────────────────

def minimal_deck() -> dict:
    return {
        "title": "Test Deck",
        "slides": [
            {"layout": "content", "id": "slide-1", "step": 1, "title": "Hello", "body": "World"},
        ],
    }


def full_deck() -> dict:
    return {
        "title": "Full Test",
        "author": "Tester",
        "theme": "black",
        "transition": "fade",
        "slides": [
            {"layout": "content", "id": "intro", "step": 1, "title": "Intro", "body": "Welcome"},
            {"layout": "content", "id": "intro", "step": 2, "title": "Intro", "body": "Continued"},
            {"layout": "two-column", "id": "cols", "step": 1, "body": "Left ||| Right"},
            {"layout": "code", "id": "code", "step": 1, "code": "print(1)", "language": "python"},
            {"layout": "image", "id": "img", "step": 1, "title": "Photo", "image_url": "pic.jpg"},
            {"layout": "raw", "id": "raw", "step": 1, "body": "<p>raw</p>"},
        ],
    }


# ── T002-T005: Pydantic Models ──────────────────────────────────────────

class TestLayoutType:
    def test_valid_values(self):
        for v in ("content", "two-column", "auto-animate-pair", "code", "image", "raw"):
            s = SlideRecord(layout=v, id="x", title="t")
            assert s.layout == v

    def test_invalid_value(self):
        with pytest.raises(ValidationError):
            SlideRecord(layout="bogus", id="x", title="t")


class TestSlideRecord:
    def test_minimal(self):
        s = SlideRecord(layout="content", id="s1", title="Hello")
        assert s.title == "Hello"
        assert s.step == 1

    def test_empty_content_raises(self):
        with pytest.raises(ValidationError, match="title, body, code"):
            SlideRecord(layout="content", id="s1")

    def test_raw_allows_empty(self):
        s = SlideRecord(layout="raw", id="s1")
        assert s.layout == "raw"

    def test_code_only(self):
        s = SlideRecord(layout="code", id="s1", code="print(1)", language="python")
        assert s.code == "print(1)"

    def test_body_only(self):
        s = SlideRecord(layout="content", id="s1", body="just body")
        assert s.body == "just body"

    def test_all_fields(self):
        s = SlideRecord(
            layout="content", id="s1", step=2, title="T", body="B",
            notes="N", image_url="img.jpg", code="c", language="py",
            media={"type": "video"}, fragment_order=1,
        )
        assert s.step == 2
        assert s.notes == "N"


class TestDeckData:
    def test_minimal(self):
        d = DeckData(title="D", slides=[SlideRecord(layout="content", id="s1", title="T")])
        assert d.title == "D"

    def test_requires_title(self):
        with pytest.raises(ValidationError):
            DeckData(title="", slides=[])

    def test_multiple_slides(self):
        slides = [
            SlideRecord(layout="content", id="s1", title="A"),
            SlideRecord(layout="raw", id="s2"),
        ]
        d = DeckData(title="D", slides=slides)
        assert len(d.slides) == 2


class TestResolvedSlide:
    def test_defaults(self):
        r = ResolvedSlide(layout="content", id="s1", step=1)
        assert r.fragment_index == 1
        assert r.auto_animate is False
        assert r.element_ids == {}

    def test_all_fields(self):
        r = ResolvedSlide(
            layout="content", id="s1", step=1, data_id="slide-s1-1",
            element_ids={"title": "el-s1-title"},
            auto_animate=True, auto_animate_group_id="group-s1",
            fragment_index=3,
        )
        assert r.data_id == "slide-s1-1"
        assert r.fragment_index == 3


# ── T006-T008: US1 Validation ───────────────────────────────────────────

class TestUS1Validation:
    def test_all_six_layouts(self):
        data = {
            "title": "All Layouts",
            "slides": [
                {"layout": "content", "id": "1", "title": "C"},
                {"layout": "two-column", "id": "2", "body": "L ||| R"},
                {"layout": "auto-animate-pair", "id": "3", "step": 1, "title": "A"},
                {"layout": "auto-animate-pair", "id": "3", "step": 2, "title": "B"},
                {"layout": "code", "id": "4", "code": "x"},
                {"layout": "image", "id": "5", "title": "Img", "image_url": "x.jpg"},
                {"layout": "raw", "id": "6"},
            ],
        }
        deck = DeckData.model_validate(data)
        assert len(deck.slides) == 7

    def test_invalid_layout_rejected(self):
        data = {"title": "Bad", "slides": [{"layout": "bogus", "id": "1", "title": "X"}]}
        with pytest.raises(ValidationError):
            DeckData.model_validate(data)

    def test_empty_slide_rejected(self):
        data = {"title": "Empty", "slides": [{"layout": "content", "id": "1"}]}
        with pytest.raises(ValidationError):
            DeckData.model_validate(data)


# ── T009-T014: US2 Macro Tests ──────────────────────────────────────────

MACROS_PATH = _find_macros()


class TestContentMacro:
    def test_renders_section(self):
        data = {"title": "T", "slides": [{"layout": "content", "id": "s1", "title": "Hello", "body": "World"}]}
        html = render_deck(data, MACROS_PATH)
        assert "data-id=" in html
        assert "Hello" in html
        assert "World" in html

    def test_notes_rendered(self):
        data = {"title": "T", "slides": [{"layout": "content", "id": "s1", "title": "T", "notes": "Check this"}]}
        html = render_deck(data, MACROS_PATH)
        assert "Check this" in html

    def test_empty_title_renders(self):
        data = {"title": "T", "slides": [{"layout": "content", "id": "s1", "body": "B"}]}
        html = render_deck(data, MACROS_PATH)
        assert "B" in html


class TestTwoColumnMacro:
    def test_split_body(self):
        data = {"title": "T", "slides": [{"layout": "two-column", "id": "c1", "body": "Left ||| Right"}]}
        html = render_deck(data, MACROS_PATH)
        assert "col" in html
        assert "Left" in html
        assert "Right" in html

    def test_three_parts_uses_first_two(self):
        data = {"title": "T", "slides": [{"layout": "two-column", "id": "c1", "body": "A ||| B ||| C"}]}
        html = render_deck(data, MACROS_PATH)
        assert "A" in html
        assert "B" in html


class TestCodeMacro:
    def test_code_block_rendered(self):
        data = {"title": "T", "slides": [{"layout": "code", "id": "c1", "code": "def f(): pass", "language": "python"}]}
        html = render_deck(data, MACROS_PATH)
        assert "language-python" in html
        assert "def f(): pass" in html

    def test_code_no_language(self):
        data = {"title": "T", "slides": [{"layout": "code", "id": "c1", "code": "hello"}]}
        html = render_deck(data, MACROS_PATH)
        assert "hello" in html


class TestImageMacro:
    def test_background_image(self):
        data = {"title": "T", "slides": [{"layout": "image", "id": "i1", "image_url": "pic.jpg"}]}
        html = render_deck(data, MACROS_PATH)
        assert "pic.jpg" in html
        assert "data-background-image" in html

    def test_title_overlaid(self):
        data = {"title": "T", "slides": [{"layout": "image", "id": "i1", "image_url": "pic.jpg", "title": "Overlay"}]}
        html = render_deck(data, MACROS_PATH)
        assert "Overlay" in html


class TestRawMacro:
    def test_body_verbatim(self):
        data = {"title": "T", "slides": [{"layout": "raw", "id": "r1", "body": "<section><p>custom</p></section>"}]}
        html = render_deck(data, MACROS_PATH)
        assert "<p>custom</p>" in html


# ── T015-T021: US3 Resolver Tests ───────────────────────────────────────

class TestResolverGroups:
    def test_matching_data_id_in_pair(self):
        data = {
            "title": "T",
            "slides": [
                {"layout": "auto-animate-pair", "id": "tense", "step": 1, "title": "A"},
                {"layout": "auto-animate-pair", "id": "tense", "step": 2, "title": "B"},
            ],
        }
        result = resolve_deck(data)
        group = [s for s in result["slides"] if s["layout"] == "auto-animate-pair"]
        assert len(group) == 2
        for s in group:
            assert s["auto_animate"] is True
            assert s["auto_animate_group_id"] == "group-tense"
        assert group[0]["element_ids"] == group[1]["element_ids"]

    def test_sequential_fragment_index(self):
        data = {
            "title": "T",
            "slides": [
                {"layout": "content", "id": "a", "title": "A"},
                {"layout": "content", "id": "b", "title": "B"},
                {"layout": "content", "id": "c", "title": "C"},
            ],
        }
        result = resolve_deck(data)
        indices = [s["fragment_index"] for s in result["slides"]]
        assert indices == [1, 2, 3]

    def test_single_slide_no_auto_animate(self):
        data = {"title": "T", "slides": [{"layout": "content", "id": "solo", "title": "S"}]}
        result = resolve_deck(data)
        assert result["slides"][0]["auto_animate"] is False
        assert result["slides"][0]["auto_animate_group_id"] is None

    def test_group_of_three(self):
        data = {
            "title": "T",
            "slides": [
                {"layout": "auto-animate-pair", "id": "g", "step": 1, "title": "A"},
                {"layout": "auto-animate-pair", "id": "g", "step": 2, "body": "B"},
                {"layout": "auto-animate-pair", "id": "g", "step": 3, "body": "C"},
            ],
        }
        result = resolve_deck(data)
        slides = result["slides"]
        for s in slides:
            assert s["auto_animate"] is True
            assert s["auto_animate_group_id"] == "group-g"

    def test_empty_deck(self):
        data = {"title": "T", "slides": []}
        result = resolve_deck(data)
        assert result["slides"] == []

    def test_raw_no_element_ids(self):
        data = {"title": "T", "slides": [{"layout": "raw", "id": "r1", "body": "<p>raw</p>"}]}
        result = resolve_deck(data)
        assert result["slides"][0]["element_ids"] == {}
        assert result["slides"][0]["fragment_index"] == 1
        assert result["slides"][0]["data_id"] == "slide-r1-1"

    def test_auto_animate_pair_with_resolver(self):
        data = {
            "title": "T",
            "slides": [
                {"layout": "auto-animate-pair", "id": "pair", "step": 1, "title": "Before", "body": "old"},
                {"layout": "auto-animate-pair", "id": "pair", "step": 2, "title": "After", "body": "new"},
            ],
        }
        html = render_deck(data, MACROS_PATH)
        assert 'data-auto-animate' in html
        assert "Before" in html
        assert "After" in html


# ── T022-T026: Pipeline Integration ─────────────────────────────────────

class TestPipeline:
    def test_minimal_renders(self):
        data = {"title": "Minimal", "slides": [{"layout": "content", "id": "s1", "title": "Hi"}]}
        html = render_deck(data, MACROS_PATH)
        assert "<!doctype html>" in html
        assert "Hi" in html
        assert "reveal.js" in html

    def test_full_deck_renders(self):
        html = render_deck(full_deck(), MACROS_PATH)
        assert "<!doctype html>" in html
        assert "Intro" in html
        assert "Welcome" in html
        assert "Left" in html
        assert "print(1)" in html
        assert "pic.jpg" in html
        assert "<p>raw</p>" in html

    def test_theme_applied(self):
        html = render_deck(full_deck(), MACROS_PATH)
        assert "theme/black.css" in html

    def test_transition_applied(self):
        html = render_deck(full_deck(), MACROS_PATH)
        assert '"fade"' in html

    def test_data_id_on_section(self):
        data = {"title": "T", "slides": [{"layout": "content", "id": "intro", "title": "X"}]}
        html = render_deck(data, MACROS_PATH)
        assert 'data-id="slide-intro-1"' in html

    def test_fragment_index_on_section(self):
        data = {"title": "T", "slides": [{"layout": "content", "id": "a", "title": "A"}, {"layout": "content", "id": "b", "title": "B"}]}
        html = render_deck(data, MACROS_PATH)
        assert 'data-fragment-index="1"' in html
        assert 'data-fragment-index="2"' in html
