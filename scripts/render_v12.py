#!/usr/bin/env python3
"""Measure hero vertical rhythm at several viewports: gaps nav->wordmark,
wordmark->content, content->bottom. Capture the hero for visual tuning."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
VPS = [(1440,900),(1440,1080),(1920,1320),(390,844)]
with sync_playwright() as p:
    b = p.chromium.launch()
    for w,h in VPS:
        pg = b.new_page(viewport={"width":w,"height":h})
        pg.goto(URL, wait_until="domcontentloaded")
        try: pg.wait_for_selector("#hero.revealed", timeout=9000)
        except Exception: pass
        time.sleep(4.6)  # let wordmark settle
        m = pg.evaluate("""()=>{
          const r=s=>{const e=document.querySelector(s);return e?e.getBoundingClientRect():null;};
          const nav=r('.nav'), logo=r('.hero-logo'), wrap=r('.hero .wrap'),
                copy=r('.hero .copy'), port=r('.portrait-stage'), hero=r('#hero');
          const g=(a,b)=>a&&b?Math.round(b-a):null;
          return {vh:innerHeight,
            navBottom:Math.round(nav.bottom),
            logoTop:Math.round(logo.top), logoBottom:Math.round(logo.bottom), logoH:Math.round(logo.height),
            wrapTop:Math.round(wrap.top), wrapBottom:Math.round(wrap.bottom),
            gap_nav_to_logo:g(nav.bottom, logo.top),
            gap_logo_to_wrap:g(logo.bottom, wrap.top),
            gap_wrap_to_vh: Math.round(innerHeight - wrap.bottom),
            heroH:Math.round(hero.height)};
        }""")
        print(f"{w}x{h}:", m)
        tag=f"{w}x{h}"
        pg.evaluate("scrollTo(0,0)"); time.sleep(0.3)
        pg.screenshot(path=str(OUT/f"v12_hero_{tag}.png"))
        pg.close()
    b.close()
