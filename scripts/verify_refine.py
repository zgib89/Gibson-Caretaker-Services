#!/usr/bin/env python3
"""Targeted checks for the 'perfect it' refinement pass:
  A) canvas-defer: a below-fold season card must START animating once scrolled in
  B) hero <em> contrast: measure bg behind the gradient em vs its LIGHTEST stop
     (#e6207e), desktop AND mobile, across a few aurora frames; report the
     applicable WCAG threshold from the em's computed size
  C) SOFT axis: heading weight held (==500) + font actually loaded
  D) icon-contrast fix: white on Summer/Winter .item .ic now clears the 3:1 floor
"""
import sys, json, statistics
from playwright.sync_api import sync_playwright

URL = "file:///" + r"C:\Users\zacgi\Gibson-Caretaker-Services\public\index.html".replace("\\", "/")


def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(r, g, b):
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(l1, l2):
    a, b = max(l1, l2), min(l1, l2)
    return (a + 0.05) / (b + 0.05)


PINK = lum(230, 32, 126)  # #e6207e lightest gradient stop


def region_contrast_stats(png_bytes, text_lum):
    """Robust: median + 10th-percentile contrast + fraction of area below 3:1,
    over the bg behind the (hidden) em. Avoids single-pixel antialias outliers."""
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    px = im.load()
    cs = []
    for y in range(0, im.height, 2):
        for x in range(0, im.width, 2):
            r, g, b = px[x, y]
            cs.append(contrast(text_lum, lum(r, g, b)))
    cs.sort()
    n = len(cs)
    median = cs[n // 2]
    p10 = cs[max(0, n // 10)]
    frac_below3 = sum(1 for c in cs if c < 3.0) / n
    return round(median, 2), round(p10, 2), round(frac_below3, 3)


def canvas_hash(page, sel):
    # hash the WHOLE canvas (coarse stride) so any motion anywhere is detected,
    # not just a static sky corner
    return page.eval_on_selector(sel,
        "c=>{const x=c.getContext('2d');if(!x||!c.width)return '';"
        "const d=x.getImageData(0,0,c.width,c.height).data;"
        "let h=0;for(let i=0;i<d.length;i+=399){h=(h*31+d[i])>>>0;}return ''+h;}")


def main():
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)

        # ---- desktop pass ----
        pg = b.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(1800)
        out["console_errors"] = errs

        # C) SOFT: heading weight + font loaded
        out["h1_weight"] = pg.eval_on_selector("h1", "e=>getComputedStyle(e).fontWeight")
        out["h1_fvs"] = pg.eval_on_selector("h1", "e=>getComputedStyle(e).fontVariationSettings")
        out["h1_size_desktop"] = pg.eval_on_selector(".hero-copy h1", "e=>parseFloat(getComputedStyle(e).fontSize)")
        out["fraunces_loaded"] = pg.evaluate("()=>document.fonts.check('500 40px Fraunces')")

        # D) icon contrast: white on Summer / Winter .item .ic
        def ic_contrast(season_sel):
            bg = pg.eval_on_selector(season_sel + " .item .ic",
                "e=>getComputedStyle(e).backgroundColor")
            nums = [int(n) for n in bg.replace("rgb(", "").replace(")", "").split(",")[:3]]
            return round(contrast(lum(255, 255, 255), lum(*nums)), 2), bg
        out["icon_summer_white"] = ic_contrast("section[aria-labelledby='summer-h']")
        out["icon_winter_white"] = ic_contrast("section[aria-labelledby='winter-h']")
        out["icon_spring_white"] = ic_contrast("section[aria-labelledby='spring-h']")
        out["icon_autumn_white"] = ic_contrast("section[aria-labelledby='autumn-h']")

        # B) hero em bg contrast (desktop), 3 frames
        em = pg.query_selector(".hero-copy h1 em")
        box = em.bounding_box()
        clip = {"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]}
        pg.eval_on_selector(".hero-copy h1 em", "e=>e.style.visibility='hidden'")
        meds, p10s, fracs = [], [], []
        for _ in range(3):
            pg.wait_for_timeout(650)
            md, p1, fr = region_contrast_stats(pg.screenshot(clip=clip), PINK)
            meds.append(md); p10s.append(p1); fracs.append(fr)
        pg.eval_on_selector(".hero-copy h1 em", "e=>e.style.visibility=''")
        out["hero_em_desktop"] = {"median_min": min(meds), "p10_min": min(p10s), "frac_below3_max": max(fracs)}

        # A) hero (above fold) animates immediately
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
        hh1 = canvas_hash(pg, "#scene"); pg.wait_for_timeout(550); hh2 = canvas_hash(pg, "#scene")
        out["hero_scene_animates"] = hh1 != hh2
        # deferred winter card: STOPPED before scroll, ANIMATING after scroll-in
        winter = "section[aria-labelledby='winter-h'] canvas"
        wb1 = canvas_hash(pg, winter); pg.wait_for_timeout(550); wb2 = canvas_hash(pg, winter)
        out["winter_stopped_before_scroll"] = (wb1 == wb2)
        pg.eval_on_selector(winter, "c=>c.scrollIntoView({block:'center'})")
        pg.wait_for_timeout(1000)
        wa1 = canvas_hash(pg, winter); pg.wait_for_timeout(550); wa2 = canvas_hash(pg, winter)
        out["winter_animates_after_scroll"] = (wa1 != wa2)
        pg.close()

        # ---- mobile pass: hero em size + contrast (threshold may flip) ----
        m = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        m.goto(URL, wait_until="load")
        m.wait_for_timeout(1500)
        out["h1_size_mobile"] = m.eval_on_selector(".hero-copy h1", "e=>parseFloat(getComputedStyle(e).fontSize)")
        em = m.query_selector(".hero-copy h1 em")
        box = em.bounding_box()
        clip = {"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]}
        m.eval_on_selector(".hero-copy h1 em", "e=>e.style.visibility='hidden'")
        meds, p10s, fracs = [], [], []
        for _ in range(3):
            m.wait_for_timeout(650)
            md, p1, fr = region_contrast_stats(m.screenshot(clip=clip), PINK)
            meds.append(md); p10s.append(p1); fracs.append(fr)
        out["hero_em_mobile"] = {"median_min": min(meds), "p10_min": min(p10s), "frac_below3_max": max(fracs)}
        m.close()
        b.close()

    # thresholds: large text (>=24px @ weight>=500 ~ 18.66px bold) -> 3:1, else 4.5:1
    out["thresh_desktop"] = 3.0 if out["h1_size_desktop"] >= 24 else 4.5
    out["thresh_mobile"] = 3.0 if out["h1_size_mobile"] >= 24 else 4.5
    print("REFINE:" + json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
