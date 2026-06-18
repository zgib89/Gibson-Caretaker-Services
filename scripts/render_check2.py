#!/usr/bin/env python3
"""Targeted checks per advisor: (1) trust cards actually become visible
(opacity:0 -> .card.in via IntersectionObserver); (2) mobile season tab row
lands cleanly without overflow."""
import time, pathlib
from playwright.sync_api import sync_playwright

URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
ARGS = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]

with sync_playwright() as p:
    b = p.chromium.launch(args=ARGS)
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=9000)
    except Exception: pass
    time.sleep(0.5)
    # (1) trust cards
    pg.evaluate("document.querySelectorAll('.beat')[1].scrollIntoView({block:'center'})")
    pg.evaluate("[].forEach.call(document.querySelectorAll('.cards .card'),function(c){c.scrollIntoView&&0;});")
    pg.evaluate("document.querySelector('.cards').scrollIntoView({block:'center'})")
    time.sleep(1.6)
    pg.screenshot(path=str(OUT / "c2_cards.png"))
    cards = pg.evaluate("""()=>{
      const cs=[].slice.call(document.querySelectorAll('.cards .card'));
      return {total:cs.length, visible:cs.filter(c=>c.classList.contains('in')).length,
        opacities:cs.map(c=>getComputedStyle(c).opacity)};
    }""")
    print("CARDS:", cards)

    # (2) mobile season tabs
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.evaluate("window.scrollTo(0,0)")
    time.sleep(0.4)
    pg.evaluate("document.querySelector('.seasons .head').scrollIntoView({block:'start'})")
    pg.evaluate("window.scrollBy(0,-90)")
    time.sleep(0.6)
    pg.screenshot(path=str(OUT / "c2_seasonhead_m.png"))
    tabs = pg.evaluate("""()=>{
      const t=[].slice.call(document.querySelectorAll('.season-tabs button'));
      const r=t.map(b=>b.getBoundingClientRect());
      const wrap=document.querySelector('.season-tabs').getBoundingClientRect();
      return {vw:window.innerWidth, tabsLeft:Math.round(wrap.left), tabsRight:Math.round(wrap.right),
        tabsWidth:Math.round(wrap.width), oneRow:r.every(x=>Math.abs(x.top-r[0].top)<2),
        overflow: wrap.right>window.innerWidth+1 || wrap.left<-1,
        labels:t.map(b=>b.textContent)};
    }""")
    print("MOBILE TABS:", tabs)
    b.close()
