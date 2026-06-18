#!/usr/bin/env python3
"""Verify at true iPhone 16 Pro Max CSS width (440px): FAQ now centered (icon
pinned right, rotate-on-open works, text not under icon), drop-cap normalized,
footer centered, no overflow. Full-page capture."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
VW = 440
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":VW,"height":956})
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(4.6)
    cx = VW/2
    # FAQ: open a CLOSED item, check rotate + centering + icon clearance
    faq = pg.evaluate("""()=>{
      const dets=[].slice.call(document.querySelectorAll('.faq details'));
      const closed=dets.find(d=>!d.open); closed.querySelector('summary').click();
      const opened=closed.open;
      const pl=closed.querySelector('.pl'); const tr=getComputedStyle(pl).transform;
      const sum=closed.querySelector('summary').getBoundingClientRect();
      const plr=pl.getBoundingClientRect();
      // a long 2-line question
      const longD=dets.find(d=>d.querySelector('summary').textContent.includes('out of state'));
      const lsum=longD.querySelector('summary'); const ltext=lsum.firstChild;
      const ans=document.querySelector('.faq details[open] .ans');
      return {opened, rotates: tr!=='none' && tr!=='', plRightEdge: Math.round(VW-plr.right),
        ansTextAlign: ans?getComputedStyle(ans).textAlign:null,
        summaryTextAlign: getComputedStyle(closed.querySelector('summary')).textAlign};
    }""".replace("VW", str(VW)))
    print("FAQ:", faq)
    dc = pg.evaluate("()=>{const e=document.querySelector('.meet .bio .dc');const cs=getComputedStyle(e);return {fontSize:cs.fontSize, float:cs.float, color:cs.color};}")
    print("DROP-CAP:", dc)
    ov = pg.evaluate("()=>document.documentElement.scrollWidth>innerWidth+1")
    print("overflowX:", ov)

    # shots
    pg.evaluate("document.querySelector('.faq').scrollIntoView({block:'center'})"); time.sleep(0.6)
    pg.screenshot(path=str(OUT/"x440_faq.png"))
    pg.evaluate("document.querySelector('.meet').scrollIntoView({block:'start'})"); time.sleep(0.5)
    pg.screenshot(path=str(OUT/"x440_meet.png"))
    pg.evaluate("document.querySelector('footer').scrollIntoView({block:'end'})"); time.sleep(0.5)
    pg.screenshot(path=str(OUT/"x440_footer.png"))
    # footer centering measure
    foot = pg.evaluate("""()=>{
      const f=document.querySelector('footer'); const cx=440/2;
      const brand=f.querySelector('.brand'); const r=brand.getBoundingClientRect();
      return {brandCenter:Math.round(r.left+r.width/2), vpCenter:cx, centered:Math.abs((r.left+r.width/2)-cx)<14};
    }""")
    print("FOOTER:", foot)
    pg.evaluate("scrollTo(0,0)"); time.sleep(0.3)
    pg.screenshot(path=str(OUT/"x440_full.png"), full_page=True)
    b.close()
