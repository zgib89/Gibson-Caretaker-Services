#!/usr/bin/env python3
"""Judge the design refinement at 440px: promise cards equal-height, meet chips
uniform width, unified card system, FAQ gap, towns. Measure + capture."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":440,"height":956})
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(4.6)
    m = pg.evaluate("""()=>{
      const round=x=>Math.round(x);
      const promo=[].slice.call(document.querySelectorAll('.promise .p')).map(e=>round(e.getBoundingClientRect().height));
      const chips=[].slice.call(document.querySelectorAll('.meet-chips span')).map(e=>round(e.getBoundingClientRect().width));
      const cards=['.promise .p','.step','.svc','.faq details','.review'].map(s=>{const e=document.querySelector(s);if(!e)return null;const c=getComputedStyle(e);return {sel:s,radius:c.borderTopLeftRadius};});
      return {promoHeights:promo, promoEqual: promo.length? Math.max(...promo)-Math.min(...promo)<=1 : null,
        chipWidths:chips, chipsEqual: chips.length? Math.max(...chips)-Math.min(...chips)<=1 : null,
        cardRadii:cards, overflowX: document.documentElement.scrollWidth>innerWidth+1};
    }""")
    print("PROMISE heights:", m['promoHeights'], "equal:", m['promoEqual'])
    print("MEET chip widths:", m['chipWidths'], "equal:", m['chipsEqual'])
    print("CARD radii:", [(c['sel'],c['radius']) for c in m['cardRadii'] if c])
    print("overflowX:", m['overflowX'])
    for sel,name in [("section:has(.promise)","dz_promise"),(".meet","dz_meet"),
                     ("section:has(.steps)","dz_how"),(".seasons","dz_seasons"),
                     (".faq","dz_faq"),(".area","dz_area")]:
        try:
            loc=pg.locator(sel).first; loc.scroll_into_view_if_needed(timeout=3000); time.sleep(0.4)
            loc.screenshot(path=str(OUT/f"{name}.png"))
        except Exception as e: print("skip",name,e)
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.3)
    pg.screenshot(path=str(OUT/"dz_full.png"), full_page=True)
    b.close()
