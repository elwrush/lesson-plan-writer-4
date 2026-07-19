import pytest
from slideshow_lib.globals import (
    slide_bg,
    auto_animate_pair,
    auto_animate_attrs,
    slide_transition,
    slide_visibility,
    auto_slide,
    slide_state,
    vertical_slides,
    slide_link,
    nav_button,
    preview_link,
    code_block,
    video_embed,
    audio_embed,
    iframe_embed,
    preview_image,
    preview_video,
    preview_link as preview_link_fn,
    stack,
    fit_text,
    stretch,
    frame,
    html_attrs,
)


class TestSlideBg:
    def test_color(self):
        result = slide_bg(color="#09b")
        assert 'data-background-color="#09b"' in result

    def test_image(self):
        result = slide_bg(image="pic.jpg")
        assert 'data-background-image="pic.jpg"' in result

    def test_video(self):
        result = slide_bg(video="clip.mp4")
        assert 'data-background-video="clip.mp4"' in result

    def test_video_muted_default(self):
        result = slide_bg(video="clip.mp4")
        assert "data-background-video-muted" in result

    def test_gradient(self):
        result = slide_bg(gradient="radial-gradient(...)")
        assert "radial-gradient" in result

    def test_opacity(self):
        result = slide_bg(opacity=0.5)
        assert 'data-background-opacity="0.5"' in result

    def test_empty(self):
        result = slide_bg()
        assert result == ""


class TestAutoAnimate:
    def test_basic_pair(self):
        result = auto_animate_pair("<p>a</p>", "<p>b</p>")
        assert 'data-auto-animate' in result
        assert "<p>a</p>" in result
        assert "<p>b</p>" in result

    def test_with_options(self):
        result = auto_animate_pair("<p>a</p>", "<p>b</p>", easing="ease-out", duration=0.8)
        assert 'data-auto-animate-easing="ease-out"' in result
        assert 'data-auto-animate-duration="0.8"' in result

    def test_restart(self):
        result = auto_animate_pair("<p>a</p>", "<p>b</p>", restart=True)
        assert "data-auto-animate-restart" in result

    def test_attrs_default(self):
        result = auto_animate_attrs()
        assert "data-auto-animate" in result

    def test_attrs_custom(self):
        result = auto_animate_attrs(easing="ease-in", duration=1.0)
        assert 'data-auto-animate-easing="ease-in"' in result
        assert 'data-auto-animate-duration="1.0"' in result


class TestSlideTransition:
    def test_valid(self):
        result = slide_transition(transition="fade")
        assert 'data-transition="fade"' in result

    def test_speed(self):
        result = slide_transition(speed="slow")
        assert 'data-transition-speed="slow"' in result

    def test_bg_transition(self):
        result = slide_transition(bg_transition="zoom")
        assert 'data-background-transition="zoom"' in result

    def test_empty(self):
        result = slide_transition()
        assert result == ""


class TestSlideVisibility:
    def test_hidden(self):
        assert 'hidden' in slide_visibility(hidden=True)

    def test_uncounted(self):
        assert 'uncounted' in slide_visibility(uncounted=True)

    def test_default(self):
        assert slide_visibility() == ""


class TestAutoSlide:
    def test_ms(self):
        assert 'data-autoslide="3000"' in auto_slide(3000)


class TestSlideState:
    def test_state(self):
        assert 'data-state="custom"' in slide_state("custom")

    def test_escape(self):
        result = slide_state('a"b')
        assert "&quot;" in result


class TestVerticalSlides:
    def test_wraps(self):
        result = vertical_slides("<p>a</p>", "<p>b</p>")
        assert result.startswith("<section>")
        assert result.endswith("</section>")
        assert "<p>a</p>" in result
        assert "<p>b</p>" in result


class TestLinks:
    def test_slide_link(self):
        assert 'href="#/my-slide"' in slide_link("#/my-slide")

    def test_nav_button_valid(self):
        assert 'navigate-prev' in nav_button("prev")

    def test_nav_button_invalid(self):
        assert 'navigate-next' in nav_button("bogus")

    def test_preview_link_url(self):
        result = preview_link("https://x.com")
        assert 'data-preview-link="https://x.com"' in result

    def test_preview_link_fit(self):
        result = preview_link("https://x.com", fit=True)
        assert "data-preview-fit" in result


class TestCodeBlock:
    def test_basic(self):
        result = code_block("def f(): pass")
        assert "<pre>" in result
        assert "<code" in result
        assert "def f(): pass" in result

    def test_with_language(self):
        result = code_block("print(1)", language="python")
        assert 'language-python' in result

    def test_line_numbers(self):
        result = code_block("a\nb", line_numbers="1,2")
        assert 'data-line-numbers="1,2"' in result

    def test_trim_default(self):
        result = code_block("x")
        assert "data-trim" in result

    def test_noescape(self):
        result = code_block("x", noescape=True)
        assert "data-noescape" in result

    def test_highlights(self):
        result = code_block("x", highlights="3,8-10")
        assert 'data-highlight="3,8-10"' in result


class TestMedia:
    def test_video(self):
        result = video_embed("clip.mp4")
        assert "<video" in result
        assert 'data-src="clip.mp4"' in result
        assert "data-autoplay" in result

    def test_audio(self):
        result = audio_embed("sound.mp3")
        assert "<audio" in result
        assert 'data-src="sound.mp3"' in result

    def test_iframe(self):
        result = iframe_embed("https://example.com")
        assert "<iframe" in result
        assert 'data-src="https://example.com"' in result

    def test_no_autoplay(self):
        result = video_embed("clip.mp4", autoplay=False)
        assert "data-autoplay" not in result

    def test_preload(self):
        result = audio_embed("s.mp3", preload=True)
        assert "data-preload" in result


class TestLightbox:
    def test_preview_image(self):
        assert 'img.jpg' in preview_image("img.jpg")

    def test_preview_video(self):
        assert 'vid.mp4' in preview_video("vid.mp4")

    def test_preview_link(self):
        result = preview_link_fn("https://x.com", fit=True)
        assert 'data-preview-link="https://x.com"' in result
        assert "data-preview-fit" in result


class TestLayout:
    def test_stack(self):
        result = stack("<p>a</p>", "<p>b</p>")
        assert 'r-stack' in result
        assert "<p>a</p>" in result

    def test_fit_text(self):
        result = fit_text("Hello")
        assert 'r-fit-text' in result
        assert "Hello" in result

    def test_stretch(self):
        result = stretch("<p>content</p>")
        assert 'r-stretch' in result
        assert "<p>content</p>" in result

    def test_frame(self):
        result = frame("<p>a</p>", "<p>b</p>")
        assert 'r-frame' in result


class TestHtmlAttrs:
    def test_single(self):
        result = html_attrs(easing="ease-out")
        assert 'data-easing="ease-out"' in result

    def test_multiple(self):
        result = html_attrs(a="1", b="2")
        assert 'data-a="1"' in result
        assert 'data-b="2"' in result

    def test_escape(self):
        result = html_attrs(x='a"b')
        assert "&quot;" in result
