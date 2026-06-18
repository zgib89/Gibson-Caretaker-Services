#!/usr/bin/env python3
"""Verify the audit fixes: CTA labels now large-text (>=18.66px bold => 3:1
on the gradient), mobile section padding compressed, nav-cta readable."""
import time, pathlib
from playwright.sync_api import sync_playwright

URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")

def lum(r, g, b):
    def f(c):
        c = c/255
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
def ratio(fg, bg):
    L1, L2 = lum(*fg), lum(*bg); hi, lo = max(L1, L2), min(L1, L2)
    return round((hi+0.05)/(lo+0.05), 2)

# white-on-pink contrast at each gradient stop
print("CONTRAST white on:",
      "#ff3da0", ratio((255,255,255),(255,61,160)),
      "| #e6207e", ratio((255,255,255),(230,32,126)),
      "| #bf1568", ratio((255,255,255),(191,21,104)),
      "(large-text AA needs 3.0; normal needs 4.5)")

with sync_playwright() as p:
    b = p.chromium.launch(); errs=[]
    pg = b.new_page(viewport={"width":1440,"height":900})
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror", lambda e: errs.append("ERR:"+str(e)))
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(1.5)
    pg.screenshot(path=str(OUT/"c6_hero.png"))
    info = pg.evaluate("""()=>{
      const btn=document.querySelector('.hero .btn'); const cs=getComputedStyle(btn);
      const px=parseFloat(cs.fontSize), wt=parseInt(cs.fontWeight);
      const large = (px>=18.66 && wt>=700) || px>=24;
      return {btnPx:px.toFixed(2), btnWeight:wt, qualifiesLargeText:large,
        overflowX:document.documentElement.scrollWidth>innerWidth+1};
    }""")
    print("DESKTOP btn:", info)
    # nav-cta
    pg.evaluate("scrollTo(0, innerHeight*1.4)"); time.sleep(0.5)
    nav = pg.evaluate("""()=>{const c=document.querySelector('.nav-cta');const cs=getComputedStyle(c);
      return {bg:cs.backgroundColor||cs.background.slice(0,30), px:parseFloat(cs.fontSize).toFixed(1), visible:cs.opacity};}""")
    print("NAV-CTA:", nav)

    # mobile: page height should drop vs ~ (prior full ~ longer); capture + measure
    pg.set_viewport_size({"width":390,"height":844}); pg.evaluate("scrollTo(0,0)"); time.sleep(0.6)
    mh = pg.evaluate("()=>({pageH:document.body.scrollHeight, overflowX:document.documentElement.scrollWidth>innerWidth+1})")
    print("MOBILE:", mh)
    pg.evaluate("scrollTo(0, innerHeight*1.6)"); time.sleep(0.4)
    pg.screenshot(path=str(OUT/"c6_mobile_bar.png"))
    cbh = pg.evaluate("()=>Math.round(document.querySelector('.callbar a').getBoundingClientRect().height)")
    print("MOBILE callbar btn height:", cbh)
    b.close()
    real=[e for e in errs if 'favicon' not in e and 'font' not in e.lower()]
    print("ERRORS(%d): %s"%(len(real), real[:6]))
