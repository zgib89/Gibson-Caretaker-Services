#!/usr/bin/env python3
"""Verify the PREVIEW version against the real enforced CSP before promoting:
GSAP loads (cdnjs allowlist works), zero CSP violations, all 4 images load,
wordmark/loader/sections render. Visual capture, cache-busted."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "https://80d97b0a-gibson-caretaker-services.zacgibson89.workers.dev/?v=ship1"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
with sync_playwright() as p:
    b = p.chromium.launch()
    msgs = []
    pg = b.new_page(viewport={"width":1440,"height":960})
    pg.on("console", lambda m: msgs.append((m.type, m.text)))
    pg.on("pageerror", lambda e: msgs.append(("pageerror", str(e))))
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=12000)
    except Exception as e: msgs.append(("timeout", str(e)))
    time.sleep(5.0)
    st = pg.evaluate("""()=>{
      const nat=s=>{const e=document.querySelector(s);return e?e.naturalWidth:-1;};
      return {
        gsap: typeof window.gsap, splittext: typeof window.SplitText,
        wordmark: !!document.querySelector('.wordmark'),
        sceneFn: typeof Scene, svc: document.querySelectorAll('#seaSvc .svc').length,
        reviews: !!document.querySelector('.reviews .review-empty'),
        heroRevealed: !!document.querySelector('#hero.revealed'),
        img_portrait: nat('.portrait img'),
        img_cutout: nat('.meet-photo img'),
        img_after: nat('.imbody .att img'),
        loaderGone: !document.getElementById('gcs-loader'),
        overflowX: document.documentElement.scrollWidth>innerWidth+1,
        title: document.title
      };
    }""")
    print("STATE:", st)
    pg.screenshot(path=str(OUT/"ship_hero.png"))
    for i in range(13): pg.evaluate("scrollBy(0,innerHeight*0.85)"); time.sleep(0.18)
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.4)
    pg.screenshot(path=str(OUT/"ship_full.png"), full_page=True)
    b.close()
    csp = [m for m in msgs if 'Content-Security-Policy' in m[1] or 'Refused to' in m[1] or 'violates' in m[1]]
    errs = [m for m in msgs if m[0] in ('error','pageerror') and 'favicon' not in m[1].lower()]
    print("CSP VIOLATIONS (%d):" % len(csp), csp[:6])
    print("ERRORS (%d):" % len(errs), errs[:6])
