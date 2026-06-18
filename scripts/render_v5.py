#!/usr/bin/env python3
"""Verify: hydrangea now landscape, desktop header CTA fades in on scroll (no
phone overlap), bottom bar mobile-only."""
import time, pathlib
from playwright.sync_api import sync_playwright

URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")

with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERR: " + str(e)))
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(0.5)
    # scroll to proof
    pg.evaluate("document.querySelector('.proof').scrollIntoView({block:'center'})"); time.sleep(0.8)
    pg.screenshot(path=str(OUT / "c5_proof.png"))
    pg.locator(".iphone").screenshot(path=str(OUT / "c5_iphone.png"))
    st = pg.evaluate("""()=>{
      const att=document.querySelector('.imbody .att img');
      const cta=document.querySelector('.nav-cta'); const cs=getComputedStyle(cta);
      const cb=document.getElementById('callbar');
      return {attRatio:(att.clientWidth/att.clientHeight).toFixed(3), attW:Math.round(att.clientWidth), attH:Math.round(att.clientHeight),
        bodyScrolled:document.body.classList.contains('scrolled'),
        navCtaDisplay:cs.display, navCtaOpacity:cs.opacity,
        callbarDisplay:getComputedStyle(cb).display, overflowX:document.documentElement.scrollWidth>innerWidth+1};
    }""")
    print("DESKTOP:", st, "(att ideal ~1.500)")
    # capture the nav with CTA
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.3); pg.evaluate("scrollTo(0, innerHeight*1.4)"); time.sleep(0.6)
    pg.screenshot(path=str(OUT / "c5_nav.png"), clip={"x":0,"y":0,"width":1440,"height":80})

    # mobile bottom bar
    pg.set_viewport_size({"width":390,"height":844}); pg.evaluate("scrollTo(0,0)"); time.sleep(0.5)
    pg.evaluate("scrollTo(0, innerHeight*1.6)"); time.sleep(0.5)
    mb = pg.evaluate("""()=>{const cb=document.getElementById('callbar');const r=cb.getBoundingClientRect();
      return {display:getComputedStyle(cb).display, shown:cb.classList.contains('show'), width:Math.round(r.width), full:r.width>innerWidth*0.9};}""")
    print("MOBILE bar:", mb)
    b.close()
    real=[e for e in errs if 'favicon' not in e and 'font' not in e.lower()]
    print("ERRORS(%d): %s" % (len(real), real[:6]))
