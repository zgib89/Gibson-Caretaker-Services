#!/usr/bin/env python3
"""Inject the live site's flower-to-letter wordmark (SVG + CSS) into the concept
at the <!--WORDMARK_SVG--> and /*WORDMARK_CSS*/ markers. Concept-only."""
import pathlib, sys
LIVE = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\public\index.html")
CONCEPT = pathlib.Path(r"C:\Users\zacgi\Downloads\gcs-concept.html")
live = LIVE.read_text(encoding="utf-8").split("\n")

svg = live[774]                       # line 775: the <svg class="wordmark"> ... </svg>
css = "\n".join(live[348:394])        # lines 349-394: .gl/.wm-sub/anchors/base/intro/keyframes
assert 'class="wordmark"' in svg, "SVG line mismatch"
assert '@keyframes gxSway' in css, "CSS range mismatch"

html = CONCEPT.read_text(encoding="utf-8")
for marker, payload in [("<!--WORDMARK_SVG-->", svg), ("/*WORDMARK_CSS*/", css)]:
    if marker not in html:
        print("MISSING MARKER:", marker); sys.exit(1)
    html = html.replace(marker, payload)
CONCEPT.write_text(html, encoding="utf-8")
print("injected wordmark: svg=%d chars, css=%d lines -> %d bytes"
      % (len(svg), css.count(chr(10))+1, len(html)))
