#!/usr/bin/env python3
"""Diagnose at 440px (live): footer brand centering, brand wrap, descender clip
on the headline. Capture nav, headline, footer."""
import time, pathlib
from playwright.sync_api import sync_playwright
URL = "https://gibsoncaretakerservices.com/?v=diag1"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":440,"height":956})
    pg.goto(URL, wait_until="domcontentloaded")
    try: pg.wait_for_selector("#hero.revealed", timeout=12000)
    except Exception: pass
    time.sleep(5.0)
    # nav (top)
    pg.screenshot(path=str(OUT/"diag_nav.png"), clip={"x":0,"y":0,"width":440,"height":120})
    # headline
    pg.evaluate("document.querySelector('.headline').scrollIntoView({block:'center'})"); time.sleep(0.5)
    pg.screenshot(path=str(OUT/"diag_headline.png"))
    # footer
    pg.evaluate("document.querySelector('footer').scrollIntoView({block:'end'})"); time.sleep(0.5)
    pg.screenshot(path=str(OUT/"diag_footer.png"))
    info = pg.evaluate("""()=>{
      const cx=440/2;
      const fb=document.querySelector('footer .brand'); const r=fb?fb.getBoundingClientRect():null;
      const nav=document.querySelector('.nav .brand'); const nr=nav.getBoundingClientRect();
      const navLines=Math.round(nr.height/ (parseFloat(getComputedStyle(nav).fontSize)*1.2));
      return {
        footerBrandCenter: r?Math.round(r.left+r.width/2):null, vpCenter:cx,
        footerBrandCentered: r?Math.abs((r.left+r.width/2)-cx)<14:null,
        footerBrandJustify: fb?getComputedStyle(fb).justifyContent:null,
        footerBrandTextAlign: fb?getComputedStyle(fb).textAlign:null,
        navBrandHeight: Math.round(nr.height), navBrandWidth: Math.round(nr.width),
        navBrandWraps: nr.height>40
      };
    }""")
    print(info)
    b.close()
