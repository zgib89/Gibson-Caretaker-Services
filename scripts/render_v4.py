#!/usr/bin/env python3
"""Verify the targeted fixes: meet cutout aspect-lock, iMessage phone + real
photo, compact desktop sticky bar (was full-width slab), mobile bar."""
import time, pathlib
from playwright.sync_api import sync_playwright

URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")

with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(0.6)

    pg.evaluate("document.querySelector('.meet').scrollIntoView({block:'center'})"); time.sleep(0.6)
    pg.screenshot(path=str(OUT / "c4_meet.png"))
    pg.evaluate("document.querySelector('.proof').scrollIntoView({block:'center'})"); time.sleep(0.7)
    pg.screenshot(path=str(OUT / "c4_proof.png"))

    m = pg.evaluate("""()=>{
      const cut=document.querySelector('.meet-photo img');
      const att=document.querySelector('.imbody .att img');
      const cb=document.getElementById('callbar').getBoundingClientRect();
      const recv=document.querySelector('.bbl.recv'), sent=document.querySelector('.bbl.sent');
      return {
        cutRatio:(cut.clientWidth/cut.clientHeight).toFixed(3),
        attNW:att?att.naturalWidth:0, attShown:att?att.clientWidth>0:false,
        recvOK: !!recv, sentOK: !!sent,
        overflowX: document.documentElement.scrollWidth>innerWidth+1
      };
    }""")
    print("DESKTOP:", m, "(cut ideal 0.885)")

    # show desktop callbar
    pg.evaluate("scrollTo(0, innerHeight*2)"); time.sleep(0.6)
    pg.screenshot(path=str(OUT / "c4_callbar_d.png"))
    cbd = pg.evaluate("""()=>{const c=document.getElementById('callbar');const r=c.getBoundingClientRect();
      return {shown:c.classList.contains('show'), width:Math.round(r.width), right:Math.round(innerWidth-r.right), bottom:Math.round(innerHeight-r.bottom), full:r.width>innerWidth*0.9};}""")
    print("CALLBAR desktop:", cbd)

    # zoom the phone for detail
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.3)
    pg.evaluate("document.querySelector('.iphone').scrollIntoView({block:'center'})"); time.sleep(0.6)
    pg.locator(".iphone").screenshot(path=str(OUT / "c4_iphone.png"))

    # mobile
    pg.set_viewport_size({"width":390,"height":844}); pg.evaluate("scrollTo(0,0)"); time.sleep(0.6)
    pg.evaluate("scrollTo(0, innerHeight*1.6)"); time.sleep(0.5)
    pg.screenshot(path=str(OUT / "c4_callbar_m.png"))
    cbm = pg.evaluate("""()=>{const c=document.getElementById('callbar');const r=c.getBoundingClientRect();
      return {shown:c.classList.contains('show'), width:Math.round(r.width), full:r.width>innerWidth*0.9, btnH:Math.round(c.querySelector('a').getBoundingClientRect().height), overflowX:document.documentElement.scrollWidth>innerWidth+1};}""")
    print("CALLBAR mobile:", cbm)
    pg.evaluate("document.querySelector('.iphone').scrollIntoView({block:'center'})"); time.sleep(0.6)
    pg.screenshot(path=str(OUT / "c4_proof_m.png"))

    b.close()
    real=[e for e in errs if 'favicon' not in e and 'font' not in e.lower()]
    print("ERRORS(%d): %s" % (len(real), real[:6]))
