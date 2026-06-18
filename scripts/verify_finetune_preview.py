#!/usr/bin/env python3
"""Verify fine-tune on PREVIEW server at 440px, real CSP."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "https://gibsoncaretakerservices.com/?v=ftlive3"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
with sync_playwright() as p:
    b = p.chromium.launch(); msgs=[]
    pg = b.new_page(viewport={"width":440,"height":956})
    pg.on("console", lambda m: msgs.append((m.type,m.text)))
    pg.on("pageerror", lambda e: msgs.append(("pageerror",str(e))))
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=12000)
    except Exception: pass
    time.sleep(5.0)
    pg.evaluate("document.querySelector('footer').scrollIntoView({block:'end'})"); time.sleep(0.4)
    st = pg.evaluate("""()=>{
      const em=document.querySelector('.headline em'); const er=em.getBoundingClientRect();
      const lh=parseFloat(getComputedStyle(document.querySelector('.headline')).lineHeight);
      const fb=document.querySelector('footer .brand');
      return {emLines:Math.round(er.height/lh), footerBrandJustify:getComputedStyle(fb).justifyContent,
        overflowX:document.documentElement.scrollWidth>innerWidth+1};
    }""")
    print("FINE-TUNE:", st)
    pg.evaluate("document.querySelector('footer').scrollIntoView({block:'end'})"); time.sleep(0.4)
    pg.screenshot(path=str(OUT/"ftprev_footer.png"))
    csp=[x for x in msgs if 'Content-Security-Policy' in x[1] or 'Refused to' in x[1]]
    errs=[x for x in msgs if x[0] in ('error','pageerror') and 'favicon' not in x[1].lower()]
    print("CSP(%d):"%len(csp), csp[:4]); print("ERRORS(%d):"%len(errs), errs[:4])
    b.close()
