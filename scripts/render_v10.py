#!/usr/bin/env python3
"""Verify the framed loader: framed photo + tilted frames + sprig + tagline,
on the warm aurora; reveal still works."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
for vp,tag in [({"width":1440,"height":900},"d"),({"width":390,"height":844},"m")]:
    with sync_playwright() as p:
        b = p.chromium.launch(); errs=[]
        pg = b.new_page(viewport=vp)
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.on("pageerror", lambda e: errs.append("ERR:"+str(e)))
        pg.goto(URL, wait_until="domcontentloaded")
        time.sleep(0.9)
        st = pg.evaluate("""()=>{const q=s=>document.querySelector(s);
          const f=q('.gcs-frame'), s=q('.gcs-stage'), t=q('.gcs-tag');
          return {loader:!!q('#gcs-loader'), frame:!!f, stage:!!s, tag:!!t,
            pf:document.querySelectorAll('.gcs-pf').length, sprig:!!q('.gcs-sprig'),
            frameW: f?Math.round(f.getBoundingClientRect().width):0,
            frameH: f?Math.round(f.getBoundingClientRect().height):0};}""")
        print(tag, "LOADER STATE:", st)
        pg.screenshot(path=str(OUT/f"v10_loader_{tag}.png"))
        if tag=="d":
            time.sleep(1.3); pg.screenshot(path=str(OUT/"v10_loader_d2.png"))
            # wait teardown
            gone=False
            for _ in range(60):
                if pg.evaluate("()=>!document.getElementById('gcs-loader')"): gone=True; break
                time.sleep(0.1)
            print("  loader gone:", gone)
            try: pg.wait_for_selector("#hero.revealed", timeout=4000)
            except Exception: pass
            print("  hero revealed:", pg.evaluate("()=>!!document.querySelector('#hero.revealed')"))
        b.close()
        real=[e for e in errs if 'favicon' not in e and 'font' not in e.lower()]
        print(" ", tag, "ERRORS(%d): %s"%(len(real),real[:5]))
