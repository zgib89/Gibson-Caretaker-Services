#!/usr/bin/env python3
"""Full-page screenshots of index.html at mobile + desktop widths.
Usage: python shoot.py <index.html> <out_prefix>"""
import sys, pathlib
from playwright.sync_api import sync_playwright

target = pathlib.Path(sys.argv[1]).resolve().as_uri()
prefix = sys.argv[2]

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    for name, w, h in [("mobile", 390, 844), ("desktop", 1280, 900)]:
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        pg.goto(target, wait_until="load")
        pg.wait_for_timeout(1200)
        # scroll through so IntersectionObserver reveals (.rv) fire, then back to top
        pg.evaluate("""async () => {
          const step = innerHeight * 0.8;
          for (let y = 0; y < document.body.scrollHeight; y += step) {
            window.scrollTo(0, y); await new Promise(r => setTimeout(r, 120));
          }
          window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 300));
        }""")
        pg.wait_for_timeout(500)
        pg.screenshot(path=f"{prefix}_{name}.png", full_page=True)
        print(f"wrote {prefix}_{name}.png")
        pg.close()
    b.close()
