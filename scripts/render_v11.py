#!/usr/bin/env python3
"""Verify: hero wordmark (flower-to-letter) mounts + animates, sub/trust removed,
Meet-Mariah new bio (Sienna Crest), Reviews section present, no overflow."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
with sync_playwright() as p:
    b = p.chromium.launch(); errs=[]
    pg = b.new_page(viewport={"width":1440,"height":960})
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror", lambda e: errs.append("ERR:"+str(e)))
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(1.4)
    pg.screenshot(path=str(OUT/"v11_hero_mid.png"))   # wordmark growing
    time.sleep(4.0)
    pg.screenshot(path=str(OUT/"v11_hero_set.png"))   # wordmark settled
    st = pg.evaluate("""()=>{
      const wm=document.querySelector('.wordmark'); const hl=document.querySelector('.hero-logo');
      return {
        wordmark:!!wm, heroLogo:!!hl, introClass: wm?wm.classList.contains('intro'):false,
        wmW: wm?Math.round(wm.getBoundingClientRect().width):0,
        wmH: wm?Math.round(wm.getBoundingClientRect().height):0,
        noSub: !document.querySelector('.hero .sub'),
        noTrust: !document.querySelector('.hero .trust'),
        bioSienna: (document.querySelector('.meet .bio')||{}).textContent.indexOf('Sienna Crest')>-1,
        noSlots: document.querySelectorAll('.meet .slot').length,
        reviews: !!document.querySelector('.reviews .review-empty'),
        overflowX: document.documentElement.scrollWidth>innerWidth+1
      };
    }""")
    print("STATE:", st)
    pg.evaluate("document.querySelector('.meet').scrollIntoView({block:'center'})"); time.sleep(0.6)
    pg.screenshot(path=str(OUT/"v11_meet.png"))
    pg.evaluate("document.querySelector('.reviews').scrollIntoView({block:'center'})"); time.sleep(0.6)
    pg.screenshot(path=str(OUT/"v11_reviews.png"))
    # zoom the wordmark
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.4)
    try: pg.locator(".hero-logo").screenshot(path=str(OUT/"v11_wordmark.png"))
    except Exception as e: print("wm shot skip", e)
    b.close()
    real=[e for e in errs if 'favicon' not in e and 'font' not in e.lower()]
    print("ERRORS(%d): %s"%(len(real),real[:8]))
