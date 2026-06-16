#!/usr/bin/env python3
"""Visual confirmation crops for the refinement pass."""
from playwright.sync_api import sync_playwright

URL = "file:///" + r"C:\Users\zacgi\Gibson-Caretaker-Services\public\index.html".replace("\\", "/")
OUT = r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(2000)
    # hero (wordmark + h1 + buttons + SOFT serif warmth)
    pg.screenshot(path=OUT + r"\refine_hero.png")
    # summer dark act — white icons must be visible now; seam blend above
    pg.eval_on_selector("section[aria-labelledby='summer-h']", "e=>e.scrollIntoView({block:'start'})")
    pg.wait_for_timeout(900)
    pg.screenshot(path=OUT + r"\refine_summer.png")
    # gardener bio (drop-cap + SOFT) and the seam into it
    pg.eval_on_selector("#about", "e=>e.scrollIntoView({block:'start'})")
    pg.wait_for_timeout(700)
    pg.screenshot(path=OUT + r"\refine_about.png")
    pg.close()
    b.close()
    print("shot: refine_hero.png, refine_summer.png, refine_about.png")
