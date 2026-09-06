#!/usr/bin/env python3
"""test_markdown_gate.py — RED-GATE validation for Fish Audio TTS.

Tests that assert_no_markdown() BLOCKS any text containing markdown artifacts,
and ALLOWS clean text through. This is the safety net that prevents expensive
re-generation of audio with "asterisk" read aloud.

Run: python3 test_markdown_gate.py
Exit 0 = all GREEN (clean text passes). Exit 1 = RED (markdown detected).
"""

import sys
from pathlib import Path

# Add parent dir to path so we can import generate_audio
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_audio import strip_markdown, assert_no_markdown

PASS = 0
FAIL = 0


def green(label: str, text: str):
    """Assert clean text PASSES the gate."""
    global PASS, FAIL
    try:
        assert_no_markdown(text, context=label)
        PASS += 1
        print(f"  GREEN  {label}")
    except RuntimeError as e:
        FAIL += 1
        print(f"  RED    {label} — FALSE POSITIVE: {e}")


def red(label: str, text: str):
    """Assert markdown text is BLOCKED by the gate."""
    global PASS, FAIL
    try:
        assert_no_markdown(text, context=label)
        FAIL += 1
        print(f"  RED    {label} — GATE FAILED TO BLOCK: {text!r}")
    except RuntimeError:
        PASS += 1
        print(f"  GREEN  {label} — correctly blocked")


def red_stripped(label: str, raw: str):
    """Assert strip_markdown() + gate BOTH work on markdown input."""
    global PASS, FAIL
    try:
        cleaned = strip_markdown(raw)
        assert_no_markdown(cleaned, context=label)
        PASS += 1
        print(f"  GREEN  {label} — stripped and passed")
    except RuntimeError as e:
        FAIL += 1
        print(f"  RED    {label} — STRIP FAILED: {e}")


print("=== RED-GATE: markdown artifact detection ===\n")

print("--- MUST BLOCK (raw markdown) ---")
red("**bold text**", "**bold text**")
red("*italic text*", "*italic text*")
red("__bold__", "__bold__")
red("_italic_", "_italic_")
red("`code`", "`code`")
red("![alt](url)", "![alt](url)")
red("[text](url)", "[text](url)")
red("# Heading", "# Heading")
red("> blockquote", "> quote text")
red("***bold italic***", "***bold italic***")

print("\n--- MUST PASS (clean speech text) ---")
green("simple sentence", "Hello, welcome to the show.")
green("apostrophe", "It's a beautiful day outside.")
green("hyphen", "This is a well-known fact.")
green("colon", "The answer is: forty-two.")
green("semicolon", "First, we listen; then we discuss.")
green("ellipsis", "Well... I'm not sure about that.")
green("parenthetical", "Bangkok (the old name was Krung Thep) is beautiful.")
green("em dash", "The result — a complete disaster — was obvious.")
green("slash", "He or she should decide.")
green("ampersand", "Jack & Ebony are the hosts.")
green("percent", "About fifty percent of people agreed.")
green("dollar sign", "The cost was two hundred million dollars.")
green("numbers", "In 1842, the Treaty of Nanking was signed.")
green("capital letters", "The British Empire was very powerful.")
green("question mark", "Is colonisation ever justified?")
green("exclamation", "That's incredible!")
green("quotes in speech", "He said, welcome back.")
green("numbers with commas", "Sixty-five thousand people were affected.")

print("\n--- STRIP + PASS (markdown → clean) ---")
red_stripped("strip bold", "The **answer** is forty-two.")
red_stripped("strip italic", "She *loved* the idea.")
red_stripped("strip link", "See [this article](https://example.com).")
red_stripped("strip heading", "## Introduction to the topic")
red_stripped("strip image", "![diagram](image.png) shows the process.")
red_stripped("strip mixed", "**Bold** and *italic* and `code`.")
red_stripped("strip underscore", "This is __very__ important.")

print(f"\n{'='*50}")
print(f"Results: {PASS} GREEN, {FAIL} RED")
if FAIL:
    print("FAIL — red-gate has gaps. Fix assert_no_markdown patterns.")
    sys.exit(1)
else:
    print("PASS — all markdown artifacts blocked, all clean text allowed.")
    sys.exit(0)
