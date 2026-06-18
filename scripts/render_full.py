#!/usr/bin/env python3
"""Full-page capture desktop + mobile for a spacing/rhythm/flow review,
plus per-section vertical metrics (top/height/gap) to spot uneven rhythm."""
import time, pathlib, json
from playwright.sync_api import sync_playwright

URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(0.6)
    for i in range(13):
        pg.evaluate("scrollBy(0, innerHeight*0.85)"); time.sleep(0.2)
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.5)
    pg.screenshot(path=str(OUT / "c5_full.png"), full_page=True)
    # section rhythm metrics
    metrics = pg.evaluate("""()=>{
      const secs=[].slice.call(document.querySelectorAll('section, footer'));
      let last=null, out=[];
      secs.forEach(s=>{const r=s.getBoundingClientRect(); const top=r.top+scrollY;
        const cls=(s.className||s.tagName).toString().slice(0,28);
        out.push({sec:cls, top:Math.round(top), h:Math.round(r.height)});});
      return out;
    }""")
    print("SECTION RHYTHM:");
    for m in metrics: print("  ", m)
    pageH = pg.evaluate("()=>document.body.scrollHeight")
    print("PAGE HEIGHT:", pageH)

    pg.set_viewport_size({"width":390,"height":844}); pg.evaluate("scrollTo(0,0)"); time.sleep(0.6)
    for i in range(16):
        pg.evaluate("scrollBy(0, innerHeight*0.85)"); time.sleep(0.18)
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.5)
    pg.screenshot(path=str(OUT / "c5_full_m.png"), full_page=True)
    b.close()
    print("done")
