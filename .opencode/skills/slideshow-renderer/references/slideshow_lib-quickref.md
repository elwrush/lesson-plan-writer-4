# slideshow_lib Quick Reference

**Import:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".kilo" / "skills" / "slideshow-renderer" / "lib"))
from slideshow_lib import setup_jinja
setup_jinja(env)
```

## Functions Grouped by Category

### Backgrounds
| Function | Output |
|----------|--------|
| `slide_bg(color="#09b")` | `data-background-color="#09b"` |
| `slide_bg(image="pic.jpg")` | `data-background-image="pic.jpg"` |
| `slide_bg(video="clip.mp4")` | `data-background-video="clip.mp4" data-background-video-muted` |
| `slide_bg(iframe="https://x.com")` | `data-background-iframe="https://x.com"` |

Supports: `color`, `gradient`, `image`, `size`, `position`, `repeat`, `opacity`, `video`, `iframe`, `transition`

### Auto-Animate
| Function | Output |
|----------|--------|
| `auto_animate_pair(s1, s2)` | Two `<section data-auto-animate>` elements |
| `auto_animate_attrs(easing="ease-out")` | `data-auto-animate data-auto-animate-easing="ease-out"` |

### Transitions
| Function | Output |
|----------|--------|
| `slide_transition(transition="fade")` | `data-transition="fade"` |
| `slide_transition(speed="slow")` | `data-transition-speed="slow"` |

### Visibility
| Function | Output |
|----------|--------|
| `slide_visibility(hidden=True)` | `data-visibility="hidden"` |
| `slide_visibility(uncounted=True)` | `data-visibility="uncounted"` |

### Auto-Slide
| Function | Output |
|----------|--------|
| `auto_slide(3000)` | `data-autoslide="3000"` |

### States
| Function | Output |
|----------|--------|
| `slide_state("custom")` | `data-state="custom"` |

### Vertical Slides
| Function | Output |
|----------|--------|
| `vertical_slides("<p>1</p>", "<p>2</p>")` | `<section>...\n...</section>` |

### Code
| Function | Output |
|----------|--------|
| `code_block("print(1)", language="python")` | `<pre><code class="language-python" data-trim>print(1)</code></pre>` |

### Media
| Function | Output |
|----------|--------|
| `video_embed("clip.mp4")` | `<video data-src="clip.mp4" data-autoplay></video>` |
| `audio_embed("s.mp3")` | `<audio data-src="s.mp3" data-autoplay></audio>` |
| `iframe_embed("https://x.com")` | `<iframe data-src="https://x.com" data-autoplay></iframe>` |

### Layout
| Function | Output |
|----------|--------|
| `stack(...)` | `<div class="r-stack">...</div>` |
| `fit_text("Hello")` | `<h2 class="r-fit-text">Hello</h2>` |
| `stretch(...)` | `<div class="r-stretch">...</div>` |
| `frame(...)` | `<div class="r-frame">...</div>` |

### Generic
| Function | Output |
|----------|--------|
| `html_attrs(easing="out")` | `data-easing="out"` |

## Filters

| Filter | Input | Output |
|--------|-------|--------|
| `fragment("text", style="highlight-red")` | content + optional style/index | `<span class="fragment highlight-red">text</span>` |
| `notes("text")` | string | `<aside class="notes">text</aside>` |
