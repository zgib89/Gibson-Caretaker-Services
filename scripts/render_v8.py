#!/usr/bin/env python3
"""Check: does the loader actually play? + new rose nav + pink brand + the
seasons scene with the path removed."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")

with sync_playwright() as p:
    b = p.chromium.launch(); errs=[]
    pg = b.new_page(viewport={"width":1440,"height":900})
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror", lambda e: errs.append("ERR:"+str(e)))
    pg.goto(URL, wait_until="domcontentloaded")
    time.sleep(0.6)
    # is the loader visible early?
    ld = pg.evaluate("""()=>{const l=document.getElementById('gcs-loader');
      if(!l) return {exists:false};
      const cs=getComputedStyle(l); const r=l.getBoundingClientRect();
      return {exists:true, display:cs.display, opacity:cs.opacity, visibility:cs.visibility,
        w:Math.round(r.width), h:Math.round(r.height), zIndex:cs.zIndex};}""")
    print("LOADER @0.6s:", ld)
    pg.screenshot(path=str(OUT/"v8_loader.png"))
    time.sleep(1.4)
    pg.screenshot(path=str(OUT/"v8_loader2.png"))
    # wait for hero, then nav
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(1.5)
    pg.screenshot(path=str(OUT/"v8_nav.png"), clip={"x":0,"y":0,"width":1440,"height":90})
    brand = pg.evaluate("""()=>{const bs=getComputedStyle(document.querySelector('.brand'));
      const nav=getComputedStyle(document.querySelector('.nav'));
      return {brandColor:bs.color, navBg:nav.background.slice(0,60)};}""")
    print("BRAND/NAV:", brand)
    # seasons scene (path removed)
    pg.evaluate("document.querySelector('.seasons').scrollIntoView({block:'center'})"); time.sleep(2.2)
    pg.locator(".season-stage").screenshot(path=str(OUT/"v8_scene.png"))
    b.close()
    real=[e for e in errs if 'favicon' not in e and 'font' not in e.lower()]
    print("ERRORS(%d): %s"%(len(real),real[:8]))
