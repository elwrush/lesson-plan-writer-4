import pytest
from slideshow_lib.filters import fragment, notes, markdown_to_html


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


class TestMarkdownToHtml:
    def test_paragraph(self):
        result = markdown_to_html("hello world")
        assert "<p>hello world</p>" in result

    def test_bold(self):
        result = markdown_to_html("**bold** text")
        assert "<strong>bold</strong>" in result

    def test_emphasis(self):
        result = markdown_to_html("*italic*")
        assert "<em>italic</em>" in result

    def test_list(self):
        result = markdown_to_html("- item 1\n- item 2")
        assert "<li>item 1</li>" in result

    def test_code_inline(self):
        result = markdown_to_html("use `code` here")
        assert "<code>code</code>" in result

    def test_empty_string(self):
        result = markdown_to_html("")
        assert "<p></p>" in result or result == ""

    def test_extra_extensions(self):
        result = markdown_to_html("term\n: definition")
        assert "definition" in result

    def test_multiline(self):
        text = "# Header\n\nParagraph with **bold**."
        result = markdown_to_html(text)
        assert "<h1>Header</h1>" in result
        assert "<strong>bold</strong>" in result
