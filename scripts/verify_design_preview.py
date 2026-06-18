#!/usr/bin/env python3
"""Verify design refinements on the PREVIEW server at 440px, real CSP."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "https://gibsoncaretakerservices.com/?v=dzlive1"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
with sync_playwright() as p:
    b = p.chromium.launch(); msgs=[]
    pg = b.new_page(viewport={"width":440,"height":956})
    pg.on("console", lambda m: msgs.append((m.type,m.text)))
    pg.on("pageerror", lambda e: msgs.append(("pageerror",str(e))))
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=12000)
    except Exception: pass
    time.sleep(4.6)
    m = pg.evaluate("""()=>{
      const promo=[].slice.call(document.querySelectorAll('.promise .p')).map(e=>Math.round(e.getBoundingClientRect().height));
      const chips=[].slice.call(document.querySelectorAll('.meet-chips span')).map(e=>Math.round(e.getBoundingClientRect().width));
      const radii=['.promise .p','.step','.svc','.faq details','.review'].map(s=>{const e=document.querySelector(s);return e?getComputedStyle(e).borderTopLeftRadius:null;});
      return {promoEqual: Math.max(...promo)-Math.min(...promo)<=1, chipsEqual: Math.max(...chips)-Math.min(...chips)<=1,
        radiiAll18: radii.every(r=>r==='18px'), overflowX:document.documentElement.scrollWidth>innerWidth+1};
    }""")
    print("DESIGN:", m)
    pg.evaluate("document.querySelector('.promise').scrollIntoView({block:'center'})"); time.sleep(0.5)
    pg.screenshot(path=str(OUT/"dzprev_promise.png"))
    csp=[x for x in msgs if 'Content-Security-Policy' in x[1] or 'Refused to' in x[1]]
    errs=[x for x in msgs if x[0] in ('error','pageerror') and 'favicon' not in x[1].lower()]
    print("CSP(%d):"%len(csp), csp[:4]); print("ERRORS(%d):"%len(errs), errs[:4])
    b.close()
