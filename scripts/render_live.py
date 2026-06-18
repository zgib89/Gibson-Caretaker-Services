#!/usr/bin/env python3
"""Confirm the LIVE apex serves the new redesign (markers unique to the new
build) with zero errors. Cache-busted."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "https://gibsoncaretakerservices.com/?v=shiplive2"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
with sync_playwright() as p:
    b = p.chromium.launch()
    msgs=[]
    pg = b.new_page(viewport={"width":1440,"height":960})
    pg.on("console", lambda m: msgs.append((m.type, m.text)))
    pg.on("pageerror", lambda e: msgs.append(("pageerror", str(e))))
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=12000)
    except Exception as e: msgs.append(("timeout", str(e)))
    time.sleep(5.0)
    st = pg.evaluate("""()=>({
      NEW_reviews: !!document.querySelector('.reviews .review-empty'),
      NEW_iphone: !!document.querySelector('.iphone'),
      NEW_framedLoaderCSS: !!document.querySelector('style#gcs-loader-css'),
      NEW_heroWordmark: !!document.querySelector('.hero-logo .wordmark'),
      sienna: (document.querySelector('.meet .bio')||{}).textContent?.indexOf('Sienna Crest')>-1,
      afterImg: (()=>{const e=document.querySelector('.imbody .att img');return e?e.naturalWidth:-1;})(),
      gsap: typeof window.gsap, overflowX: document.documentElement.scrollWidth>innerWidth+1,
      title: document.title
    })""")
    print("LIVE STATE:", st)
    pg.screenshot(path=str(OUT/"live_hero.png"))
    b.close()
    csp=[m for m in msgs if 'Content-Security-Policy' in m[1] or 'Refused to' in m[1]]
    errs=[m for m in msgs if m[0] in ('error','pageerror') and 'favicon' not in m[1].lower()]
    print("CSP(%d):"%len(csp), csp[:5]); print("ERRORS(%d):"%len(errs), errs[:5])
