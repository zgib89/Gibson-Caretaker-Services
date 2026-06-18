#!/usr/bin/env python3
"""Verify the footer/headline fine-tune: footer brand centered, headline pink
phrase on one line, descenders clear, no overflow at 440 + 360."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in (440, 360):
        pg = b.new_page(viewport={"width":vw,"height":956})
        pg.goto(URL, wait_until="domcontentloaded")
        try: pg.wait_for_selector("#hero.revealed", timeout=9000)
        except Exception: pass
        time.sleep(5.0)
        m = pg.evaluate("""()=>{
          const em=document.querySelector('.headline em');
          const er=em.getBoundingClientRect();
          const lh=parseFloat(getComputedStyle(document.querySelector('.headline')).lineHeight);
          return {emLines: Math.round(er.height/lh), emRight: Math.round(er.right), vw:innerWidth,
            emFits: er.right<=innerWidth-4 && er.left>=4,
            overflowX: document.documentElement.scrollWidth>innerWidth+1};
        }""")
        print(f"{vw}px:", m)
        if vw==440:
            pg.evaluate("document.querySelector('.headline').scrollIntoView({block:'center'})"); time.sleep(0.5)
            pg.locator(".headline").screenshot(path=str(OUT/"ft_headline.png"))
            pg.evaluate("document.querySelector('footer').scrollIntoView({block:'end'})"); time.sleep(0.5)
            fb = pg.evaluate("""()=>{const fb=document.querySelector('footer .brand');const r=fb.getBoundingClientRect();
              const sp=fb.querySelector('span').getBoundingClientRect();
              return {justify:getComputedStyle(fb).justifyContent, contentCenter:Math.round(sp.left+ (fb.querySelector('svg').getBoundingClientRect().left? 0:0)),
                brandItemsCenter: Math.round((fb.querySelector('svg').getBoundingClientRect().left + sp.right)/2), vpCenter:220};}""")
            print("  footer brand:", fb)
            pg.screenshot(path=str(OUT/"ft_footer.png"))
        pg.close()
    b.close()
