#!/usr/bin/env python3
"""
Remove the footer CTA container (framer-esl1yf) after Framer sync.
Run this script after syncing/exporting from Framer to remove the
"Upgrade your web presence with Framer" / "Hire me on Contra" block.

Usage: python3 scripts/remove-footer-cta.py
"""

import re
import glob
import os

# Paths relative to repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MJS_FILE = os.path.join(REPO_ROOT, "CqBKBtR7I.Dy0GIrbo.mjs")


def remove_framer_esl1yf_from_runtime():
    """Remove framer-esl1yf block from Footer's children in the runtime."""
    with open(MJS_FILE, "r") as f:
        content = f.read()

    # Already applied if Footer goes directly to framer-1uotk10 (no framer-esl1yf)
    if "children:[u(y.div,{className:`framer-esl1yf`" not in content:
        return False

    # Footer has: children:[u(y.div,{className:`framer-esl1yf`...}),m(y.div,{className:`framer-1uotk10`...
    # We need: children:[m(y.div,{className:`framer-1uotk10`...
    start_marker = "children:[u(y.div,{className:`framer-esl1yf`"
    end_marker = "}),m(y.div,{className:`framer-1uotk10`"
    replacement = "children:[m(y.div,{className:`framer-1uotk10`"

    start = content.find(start_marker)
    end = content.find(end_marker, start) if start >= 0 else -1
    if start >= 0 and end >= 0:
        new_content = (
            content[:start] + replacement + content[end + len(end_marker) :]
        )
        with open(MJS_FILE, "w") as f:
            f.write(new_content)
        return True
    return False


def extract_framer_1uotk10(html):
    """Extract the framer-1uotk10 div with proper nesting."""
    start = html.find('<div class="framer-1uotk10"')
    if start < 0:
        return None, None, None
    depth = 0
    i = start
    while i < len(html):
        if html[i : i + 4] == "<div" and (
            i + 4 >= len(html) or html[i + 4] in " \t>"
        ):
            depth += 1
        elif html[i : i + 6] == "</div>":
            depth -= 1
            if depth == 0:
                return start, i + 6, html[start : i + 6]
        i += 1
    return None, None, None


def remove_esl1yf_from_html(html):
    """Remove framer-esl1yf block but keep framer-1uotk10 in footer."""
    footer_start = html.find("<footer")
    if footer_start < 0:
        return html, False

    footer_end = html.find("</footer>", footer_start) + len("</footer>")
    footer_section = html[footer_start:footer_end]

    esl_start = footer_section.find('<div class="framer-esl1yf"')
    if esl_start < 0:
        return html, False

    uotk_start, uotk_end, uotk_block = extract_framer_1uotk10(
        footer_section[esl_start:]
    )
    if uotk_block is None:
        return html, False

    uotk_start_abs = esl_start + uotk_start
    before_esl = footer_section[:esl_start]
    after_uotk = footer_section[uotk_start_abs + len(uotk_block) :]
    for _ in range(4):
        idx = after_uotk.find("</div>")
        if idx >= 0:
            after_uotk = after_uotk[idx + 6 :].lstrip()

    new_footer = before_esl + uotk_block + after_uotk
    new_html = html[:footer_start] + new_footer + html[footer_end:]
    return new_html, True


def main():
    os.chdir(REPO_ROOT)
    changes = []

    # 1. Runtime
    if remove_framer_esl1yf_from_runtime():
        changes.append("CqBKBtR7I.Dy0GIrbo.mjs")

    # 2. HTML files
    for path in glob.glob("*.html"):
        with open(path) as f:
            content = f.read()
        new_content, changed = remove_esl1yf_from_html(content)
        if changed:
            with open(path, "w") as f:
                f.write(new_content)
            changes.append(path)

    if changes:
        print("Updated:", ", ".join(changes))
    else:
        print("No changes needed (footer CTA already removed)")


if __name__ == "__main__":
    main()
