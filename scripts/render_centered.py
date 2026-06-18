#!/usr/bin/env python3
"""Verify mobile-portrait centering: the iMessage phone + step/service cards
+ section headings are horizontally centered. Captures the flagged sections."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
VW = 402
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":VW,"height":860})
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(4.6)
    cx = VW/2
    def center(sel):
        r = pg.evaluate(f"""()=>{{const e=document.querySelector('{sel}');if(!e)return null;const b=e.getBoundingClientRect();return [b.left+b.width/2,b.width];}}""")
        return r
    checks = {}
    for name, sel in [("phone",".iphone"),("step_badge",".step .n"),("svc_icon",".svc .ic"),
                      ("how_h2","section:has(.steps) h2"),("seasons_h2",".seasons h2"),
                      ("promise_ic",".promise .p .ic")]:
        r = center(sel)
        if r: checks[name] = {"center":round(r[0]),"vpCenter":round(cx),"centered":abs(r[0]-cx)<10}
    for k,v in checks.items(): print(f"  {k}: {v}")

    # screenshots of flagged sections
    for sel,name in [(".proof","cen_proof"),("section:has(.steps)","cen_how"),(".seasons","cen_seasons")]:
        try:
            loc = pg.locator(sel).first
            loc.scroll_into_view_if_needed(timeout=3000); time.sleep(0.5)
            loc.screenshot(path=str(OUT/f"{name}.png"))
        except Exception as e: print("skip",name,e)
    # full page
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.3)
    for i in range(16): pg.evaluate("scrollBy(0,innerHeight*0.85)"); time.sleep(0.15)
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.4)
    pg.screenshot(path=str(OUT/"cen_full.png"), full_page=True)
    b.close()
    print("done")
