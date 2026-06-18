#!/usr/bin/env python3
"""Verify snappier loader (time-to-teardown) + page intact after all edits."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
with sync_playwright() as p:
    b = p.chromium.launch(); errs=[]
    pg = b.new_page(viewport={"width":1440,"height":900})
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror", lambda e: errs.append("ERR:"+str(e)))
    t0=time.time()
    pg.goto(URL, wait_until="domcontentloaded")
    # poll until loader torn down
    gone_at=None
    for _ in range(120):
        if pg.evaluate("()=>!document.getElementById('gcs-loader')"):
            gone_at=time.time()-t0; break
        time.sleep(0.1)
    print("LOADER torn down at ~%.2fs after domcontentloaded" % (gone_at or -1))
    try: pg.wait_for_selector("#hero.revealed", timeout=6000)
    except Exception: pass
    time.sleep(1.5)
    state = pg.evaluate("""()=>({
      heroRevealed:!!document.querySelector('#hero.revealed'),
      brandColor:getComputedStyle(document.querySelector('.brand')).color,
      sceneFn: typeof Scene, svc: document.querySelectorAll('#seaSvc .svc').length,
      noCaption: !document.querySelector('.exnote'),
      overflowX: document.documentElement.scrollWidth>innerWidth+1
    })""")
    print("STATE:", state)
    pg.screenshot(path=str(OUT/"v9_top.png"))
    b.close()
    real=[e for e in errs if 'favicon' not in e and 'font' not in e.lower()]
    print("ERRORS(%d): %s"%(len(real),real[:8]))
