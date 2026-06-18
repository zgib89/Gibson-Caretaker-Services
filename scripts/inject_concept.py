#!/usr/bin/env python3
"""Inject the live site's proven loader (CSS + markup + JS) and the seasonal
canvas engine into the /forge concept demo. Concept-only; live site untouched."""
import pathlib, sys

LIVE = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\public\index.html")
CONCEPT = pathlib.Path(r"C:\Users\zacgi\Downloads\gcs-concept.html")

live = LIVE.read_text(encoding="utf-8").split("\n")

def block(a, b):  # 1-based inclusive
    return "\n".join(live[a-1:b])

loader_css    = block(403, 491)     # <style id="gcs-loader-css"> ... </style>
loader_markup = block(496, 610)     # <div id="gcs-loader"> ... </div>
loader_js     = block(611, 756)     # <script id="gcs-loader-js"> ... </script>
engine        = block(1055, 1122)   # helpers + S + nowSeason + setAccent + Scene

# concept is served via file:// from Downloads -> relative asset paths
for find, repl in [('/gibson-hero.webp', './gibson-hero.webp')]:
    loader_css = loader_css.replace(find, repl)
    loader_markup = loader_markup.replace(find, repl)
    loader_js = loader_js.replace(find, repl)

html = CONCEPT.read_text(encoding="utf-8")
repls = {
    "<!--LOADER_CSS-->": loader_css,
    "<!--LOADER_MARKUP-->": loader_markup + "\n" + loader_js,
    "<!--CANVAS_ENGINE-->": engine,
}
for marker, payload in repls.items():
    if marker not in html:
        print("MISSING MARKER:", marker); sys.exit(1)
    html = html.replace(marker, payload)

CONCEPT.write_text(html, encoding="utf-8")
print("injected loader_css=%d markup=%d js=%d engine=%d lines -> %d bytes"
      % (loader_css.count(chr(10)), loader_markup.count(chr(10)),
         loader_js.count(chr(10)), engine.count(chr(10)), len(html)))
