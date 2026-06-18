#!/usr/bin/env python3
"""Verify promise 2x2 on mobile + the final sticky bar (Text/Call Mariah +
icons, no crowding) render cleanly; no overflow."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
with sync_playwright() as p:
    b = p.chromium.launch(); errs=[]
    pg = b.new_page(viewport={"width":390,"height":844})
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror", lambda e: errs.append("ERR:"+str(e)))
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(0.8)
    pg.locator("section:has(.promise)").first.screenshot(path=str(OUT/"v7_promise_m.png"))
    cols = pg.evaluate("()=>getComputedStyle(document.querySelector('.promise')).gridTemplateColumns.split(' ').length")
    pg.evaluate("scrollTo(0, innerHeight*2)"); time.sleep(0.5)
    pg.screenshot(path=str(OUT/"v7_callbar_m.png"))
    # check the call button text fits (scrollWidth <= clientWidth inside button)
    fit = pg.evaluate("""()=>{
      const as=[].slice.call(document.querySelectorAll('.callbar a'));
      return as.map(a=>({txt:a.textContent.trim(), fits:a.scrollWidth<=a.clientWidth+1, h:Math.round(a.getBoundingClientRect().height)}));
    }""")
    ov = pg.evaluate("()=>document.documentElement.scrollWidth>innerWidth+1")
    print("promise cols(mobile):", cols, "| callbar:", fit, "| overflowX:", ov)
    b.close()
    real=[e for e in errs if 'favicon' not in e and 'font' not in e.lower()]
    print("ERRORS(%d): %s"%(len(real),real[:5]))
