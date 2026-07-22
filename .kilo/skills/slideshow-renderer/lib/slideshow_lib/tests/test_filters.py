import pytest
from slideshow_lib.filters import fragment, notes

class TestFragment:
    def test_fragment_default(self):
        result = fragment("hello")
        assert 'class="fragment"' in result
        assert "hello" in result

    def test_fragment_with_style(self):
        result = fragment("world", style="highlight-red")
        assert "highlight-red" in result
        assert "world" in result

    def test_fragment_with_index(self):
        result = fragment("test", index=3)
        assert 'data-fragment-index="3"' in result

    def test_fragment_unknown_style(self):
        result = fragment("x", style="bogus")
        assert "bogus" not in result

    def test_fragment_all_styles(self):
        from slideshow_lib.filters import _FRAGMENT_STYLES
        for s in _FRAGMENT_STYLES:
            result = fragment("x", style=s)
            assert s in result

class TestNotes:
    def test_notes_simple(self):
        result = notes("Check comprehension")
        assert "<aside" in result
        assert "Check comprehension" in result

    def test_notes_escapes_html(self):
        result = notes("<script>alert(1)</script>")
        assert "&lt;script&gt;" in result

    def test_notes_empty(self):
        result = notes("")
        assert "<aside" in result
