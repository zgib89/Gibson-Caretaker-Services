#!/usr/bin/env python3
"""Render-verify the /forge concept demo headless (WebGL via swiftshader).
Captures loader/hero/seasons/cutout + mobile, checks console + key state."""
import time, pathlib
from playwright.sync_api import sync_playwright

URL = "file:///C:/Users/zacgi/Downloads/gcs-concept.html"
OUT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots")
OUT.mkdir(exist_ok=True)
ARGS = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]

def run():
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
        pg.goto(URL, wait_until="domcontentloaded")
        time.sleep(1.3)
        pg.screenshot(path=str(OUT / "c2_loader.png"))           # loader mid-fill
        # wait for hero reveal (loader clears ~4s) then settle
        try:
            pg.wait_for_selector("#hero.revealed", timeout=9000)
        except Exception as e:
            errs.append("hero never revealed: %s" % e)
        loader_gone_at = time.time()
        time.sleep(2.0)
        pg.screenshot(path=str(OUT / "c2_hero.png"))             # revealed hero
        # ensure season scene exists; scroll it into view
        pg.evaluate("document.querySelector('.seasons').scrollIntoView({block:'center'})")
        time.sleep(2.2)
        pg.screenshot(path=str(OUT / "c2_seasons.png"))          # seasons explorer (spring)
        # click Winter tab -> scene should morph + services swap
        pg.evaluate("document.querySelector('.season-tabs button[data-s=\"winter\"]').click()")
        time.sleep(2.2)
        pg.screenshot(path=str(OUT / "c2_winter.png"))
        # questions / cutout
        pg.evaluate("document.querySelector('.ask').scrollIntoView({block:'center'})")
        time.sleep(0.8)
        pg.screenshot(path=str(OUT / "c2_ask.png"))

        state = pg.evaluate("""() => {
          const q=s=>document.querySelector(s);
          const cut=q('.ask .cut'), port=q('.portrait img');
          const sc=q('#seasonScene');
          return {
            glReady: !!window.__glReady,
            sceneFn: typeof Scene,
            sCount: (typeof S==='object'&&S)?Object.keys(S).length:0,
            seasonCanvasW: sc?sc.width:0, seasonCanvasH: sc?sc.height:0,
            svcCards: document.querySelectorAll('#seaSvc .svc').length,
            seaName: (q('#seaName')||{}).textContent,
            heroRevealed: !!document.querySelector('#hero.revealed'),
            portraitNW: port?port.naturalWidth:0,
            cutNW: cut?cut.naturalWidth:0,
            cutClientW: cut?Math.round(cut.clientWidth):0,
            cutClientH: cut?Math.round(cut.clientHeight):0,
            cutRatio: cut?(cut.clientWidth/cut.clientHeight).toFixed(3):0,
            loaderGone: !document.getElementById('gcs-loader')
          };
        }""")

        # mobile
        pg.set_viewport_size({"width": 390, "height": 844})
        pg.evaluate("window.scrollTo(0,0)")
        time.sleep(1.0)
        pg.screenshot(path=str(OUT / "c2_hero_m.png"))
        pg.evaluate("document.querySelector('.seasons').scrollIntoView({block:'center'})")
        time.sleep(1.2)
        pg.screenshot(path=str(OUT / "c2_seasons_m.png"))
        pg.evaluate("document.querySelector('.ask').scrollIntoView({block:'center'})")
        time.sleep(0.6)
        pg.screenshot(path=str(OUT / "c2_ask_m.png"))

        b.close()
        print("STATE:", state)
        print("CUT ideal ratio 680/768 =", round(680/768, 3))
        real = [e for e in errs if "favicon" not in e and "font" not in e.lower()]
        print("ERRORS(%d): %s" % (len(real), real[:8]))

run()
