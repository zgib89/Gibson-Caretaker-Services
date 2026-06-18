#!/usr/bin/env python3
"""Verify mobile centering on the PREVIEW server (real CSP)."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "https://gibsoncaretakerservices.com/?v=cenlive1"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
VW = 402
with sync_playwright() as p:
    b = p.chromium.launch(); msgs=[]
    pg = b.new_page(viewport={"width":VW,"height":860})
    pg.on("console", lambda m: msgs.append((m.type,m.text)))
    pg.on("pageerror", lambda e: msgs.append(("pageerror",str(e))))
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=12000)
    except Exception as e: msgs.append(("timeout",str(e)))
    time.sleep(4.6)
    cx=VW/2
    def c(sel):
        r=pg.evaluate(f"""()=>{{const e=document.querySelector('{sel}');if(!e)return null;const b=e.getBoundingClientRect();return b.left+b.width/2;}}""")
        return None if r is None else {"center":round(r),"centered":abs(r-cx)<10}
    for n,s in [("phone",".iphone"),("how_h2","section:has(.steps) h2"),("seasons_h2",".seasons h2"),("step_badge",".step .n")]:
        print(" ",n,c(s))
    pg.evaluate("document.querySelector('.proof').scrollIntoView({block:'center'})"); time.sleep(0.5)
    pg.screenshot(path=str(OUT/"prev_cen_proof.png"))
    csp=[m for m in msgs if 'Content-Security-Policy' in m[1] or 'Refused to' in m[1]]
    errs=[m for m in msgs if m[0] in ('error','pageerror') and 'favicon' not in m[1].lower()]
    print("CSP(%d):"%len(csp), csp[:4]); print("ERRORS(%d):"%len(errs), errs[:4])
    b.close()
