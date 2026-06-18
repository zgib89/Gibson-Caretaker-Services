#!/usr/bin/env python3
"""Per-section full-size screenshots, desktop + mobile, for a real visual
spacing/rhythm review (each section captured whole)."""
import time, pathlib
from playwright.sync_api import sync_playwright

URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
SECS = [
    ("#hero", "hero"),
    ("section:has(.promise)", "promise"),
    ("section:has(.meet)", "meet"),
    ("section:has(.proof)", "proof"),
    ("section:has(.steps)", "how"),
    ("section.seasons", "seasons"),
    ("section:has(.faq)", "faq"),
    ("section:has(.area)", "area"),
    ("footer", "footer"),
]

def shoot(pg, prefix):
    for sel, name in SECS:
        try:
            loc = pg.locator(sel).first
            loc.scroll_into_view_if_needed(timeout=3000); time.sleep(0.5)
            loc.screenshot(path=str(OUT / f"{prefix}_{name}.png"))
        except Exception as e:
            print("skip", name, e)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(1.4)
    shoot(pg, "d")
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.6)
    shoot(pg, "m")
    b.close()
    print("done")
