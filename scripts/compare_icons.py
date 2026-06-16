#!/usr/bin/env python3
"""Before/after crop of the Summer season-card icon chips (the most visible fix)."""
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots"
OLD = "file:///" + (OUT + r"\old_index.html").replace("\\", "/")
NEW = "file:///" + r"C:\Users\zacgi\Gibson-Caretaker-Services\public\index.html".replace("\\", "/")


def shot(pg, path):
    sec = pg.query_selector("section[aria-labelledby='summer-h']")
    sec.scroll_into_view_if_needed()
    pg.wait_for_timeout(800)
    items = pg.query_selector(".act-dark .items")
    b = items.bounding_box()
    pg.screenshot(path=path, clip={"x": b["x"], "y": b["y"], "width": b["width"], "height": b["height"]})


with sync_playwright() as p:
    br = p.chromium.launch(headless=True)
    for url, name in ((OLD, "icons_before.png"), (NEW, "icons_after.png")):
        pg = br.new_page(viewport={"width": 1000, "height": 900}, device_scale_factor=2)
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(1200)
        shot(pg, OUT + "\\" + name)
        pg.close()
    br.close()
    print("shot: icons_before.png, icons_after.png")
