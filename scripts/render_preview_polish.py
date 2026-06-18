#!/usr/bin/env python3
"""Verify FAQ centering + drop-cap on the PREVIEW server at 440px, real CSP."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "https://gibsoncaretakerservices.com/?v=pollive1"
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
    st = pg.evaluate("""()=>{
      const sum=document.querySelector('.faq summary');
      const ans=document.querySelector('.faq details[open] .ans');
      const dc=document.querySelector('.meet .bio .dc');
      return {faqSummaryCenter:getComputedStyle(sum).textAlign,
        faqAnsCenter:ans?getComputedStyle(ans).textAlign:null,
        dropcapPx:Math.round(parseFloat(getComputedStyle(dc).fontSize)),
        overflowX:document.documentElement.scrollWidth>innerWidth+1};
    }""")
    print("POLISH:", st)
    pg.evaluate("document.querySelector('.faq').scrollIntoView({block:'center'})"); time.sleep(0.6)
    pg.screenshot(path=str(OUT/"prevpol_faq.png"))
    csp=[m for m in msgs if 'Content-Security-Policy' in m[1] or 'Refused to' in m[1]]
    errs=[m for m in msgs if m[0] in ('error','pageerror') and 'favicon' not in m[1].lower()]
    print("CSP(%d):"%len(csp), csp[:4]); print("ERRORS(%d):"%len(errs), errs[:4])
    b.close()
