#!/usr/bin/env python3
"""Verify the rebuilt concept: containment at ultrawide (the dead-zone bug),
reveals firing on every section, accordion, sticky bar + prefilled SMS,
no horizontal overflow, full-page capture. No WebGL now (CSS background)."""
import time, pathlib
from playwright.sync_api import sync_playwright

URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
OUT.mkdir(exist_ok=True)

def wait_hero(pg):
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass

with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []

    # ---- ULTRAWIDE 2560: the dead-zone test ----
    pg = b.new_page(viewport={"width": 2560, "height": 1300})
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
    pg.goto(URL, wait_until="domcontentloaded"); wait_hero(pg); time.sleep(2.2)
    pg.screenshot(path=str(OUT / "c3_hero_2560.png"))
    uw = pg.evaluate("""()=>{
      const w=document.querySelector('.hero .wrap').getBoundingClientRect();
      const h=document.querySelector('.headline').getBoundingClientRect();
      const port=document.querySelector('.portrait-stage').getBoundingClientRect();
      return {vw:innerWidth, wrapLeft:Math.round(w.left), wrapRight:Math.round(w.right), wrapW:Math.round(w.width),
        headlineLeft:Math.round(h.left), portraitRight:Math.round(port.right),
        gapHeadlineToPortrait:Math.round(port.left-h.right),
        overflowX: document.documentElement.scrollWidth>innerWidth+1};
    }""")
    print("2560:", uw)

    # ---- 1920 ----
    pg.set_viewport_size({"width":1920,"height":1080}); pg.evaluate("scrollTo(0,0)"); time.sleep(1.0)
    pg.screenshot(path=str(OUT / "c3_hero_1920.png"))
    o1920 = pg.evaluate("()=>({vw:innerWidth, overflowX:document.documentElement.scrollWidth>innerWidth+1, wrapW:Math.round(document.querySelector('.hero .wrap').getBoundingClientRect().width)})")
    print("1920:", o1920)

    # ---- 1440 full page + interactions ----
    pg.set_viewport_size({"width":1440,"height":900}); pg.evaluate("scrollTo(0,0)"); time.sleep(0.6)
    # scroll through to trigger reveals
    for i in range(12):
        pg.evaluate("scrollBy(0, innerHeight*0.85)"); time.sleep(0.25)
    time.sleep(0.6)
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.5)
    pg.screenshot(path=str(OUT / "c3_full.png"), full_page=True)
    checks = pg.evaluate("""()=>{
      const rv=[].slice.call(document.querySelectorAll('.rv'));
      const det=[].slice.call(document.querySelectorAll('.faq details'));
      const smsHero=document.querySelector('.hero a[href^=\"sms:\"]').getAttribute('href');
      const smsBar=document.querySelector('#callbar a[href^=\"sms:\"]').getAttribute('href');
      const tel=document.querySelector('a[href^=\"tel:\"]').getAttribute('href');
      return {rvTotal:rv.length, rvIn:rv.filter(e=>e.classList.contains('in')).length,
        faqCount:det.length, faqOpenDefault:det.filter(d=>d.open).length,
        smsHasBody: smsHero.indexOf('body=')>-1, smsBarHasBody: smsBar.indexOf('body=')>-1,
        telOk: tel==='tel:+16083417826',
        sceneFn: typeof Scene, sCount:(typeof S==='object'&&S)?Object.keys(S).length:0,
        svcCards: document.querySelectorAll('#seaSvc .svc').length};
    }""")
    print("CHECKS:", checks)
    # accordion: open a closed one
    acc = pg.evaluate("""()=>{
      const d=document.querySelectorAll('.faq details')[2];
      d.querySelector('summary').click();
      return {nowOpen:d.open};
    }""")
    print("ACCORDION click 3rd ->", acc)
    # sticky bar after scroll
    pg.evaluate("scrollTo(0, innerHeight*2)"); time.sleep(0.4)
    barshown = pg.evaluate("()=>document.getElementById('callbar').classList.contains('show')")
    print("STICKY BAR shown after scroll:", barshown)

    # section shots at 1440
    for sel, name in [(".meet","c3_meet"),(".proof","c3_proof"),(".steps","c3_how"),(".faq","c3_faq"),(".area","c3_area")]:
        pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'center'}})"); time.sleep(0.5)
        pg.screenshot(path=str(OUT / (name+".png")))

    # ---- mobile 390 ----
    pg.set_viewport_size({"width":390,"height":844}); pg.evaluate("scrollTo(0,0)"); time.sleep(0.8)
    pg.screenshot(path=str(OUT / "c3_hero_m.png"))
    mob = pg.evaluate("()=>({overflowX:document.documentElement.scrollWidth>innerWidth+1})")
    pg.evaluate("scrollTo(0, innerHeight*1.5)"); time.sleep(0.4)
    barm = pg.evaluate("()=>document.getElementById('callbar').classList.contains('show')")
    pg.screenshot(path=str(OUT / "c3_mid_m.png"))
    print("MOBILE:", mob, "stickybar:", barm)

    b.close()
    real=[e for e in errs if 'favicon' not in e and 'font' not in e.lower()]
    print("ERRORS(%d): %s" % (len(real), real[:8]))
