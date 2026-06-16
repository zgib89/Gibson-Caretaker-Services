#!/usr/bin/env python3
"""Reconcile verify_bg (5.57) vs audit (2.8-3.3) for the assure-row captions.
The 4-col grid puts the OUTER captions (~12% / ~88%) in the .lift fade zone
(transparent 0-22% & 78-100%), where aurora bleeds through. Measure the
composite bg behind EACH caption's glyph box, across aurora frames, both
viewports. .86rem ink-faint => small text => 4.5:1 threshold."""
import sys, json
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


def stats(png, text_lum):
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(png)).convert("RGB")
    px = im.load()
    cs = []
    for y in range(0, im.height, 1):
        for x in range(0, im.width, 1):
            r, g, b = px[x, y]
            cs.append(contrast(text_lum, lum(r, g, b)))
    cs.sort()
    n = len(cs)
    return round(cs[n // 2], 2), round(cs[max(0, n // 20)], 2)  # median, p5 (robust worst)


def measure(pg, label, width):
    out = {}
    caps = pg.query_selector_all(".assure-item>span:last-child")
    # computed ink color
    col = pg.eval_on_selector(".assure-item>span:last-child", "e=>getComputedStyle(e).color")
    nums = [int(x) for x in col.replace("rgb(", "").replace(")", "").replace("a", "").split(",")[:3]]
    tlum = lum(*nums)
    out["_ink"] = col
    out["_size_px"] = pg.eval_on_selector(".assure-item>span:last-child", "e=>parseFloat(getComputedStyle(e).fontSize)")
    boxes = []
    for c in caps:
        b = c.bounding_box()
        cx = b["x"] + b["width"] / 2
        boxes.append((round(100 * cx / width, 1), b))  # center as % of viewport
    # hide all caption text, then sample each box across 3 frames
    pg.eval_on_selector_all(".assure-item>span:last-child", "els=>els.forEach(e=>e.style.visibility='hidden')")
    cols = []
    for i, (pct, b) in enumerate(boxes):
        clip = {"x": b["x"], "y": b["y"], "width": b["width"], "height": b["height"]}
        meds, p5s = [], []
        for _ in range(3):
            pg.wait_for_timeout(620)
            md, p5 = stats(pg.screenshot(clip=clip), tlum)
            meds.append(md); p5s.append(p5)
        cols.append({"col": i, "center_pct": pct, "median_min": min(meds), "p5_min": min(p5s)})
    pg.eval_on_selector_all(".assure-item>span:last-child", "els=>els.forEach(e=>e.style.visibility='')")
    out["columns"] = cols
    out["worst_p5_any_col"] = min(c["p5_min"] for c in cols)
    out["worst_median_any_col"] = min(c["median_min"] for c in cols)
    return out


def main():
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        for w in (1280, 1024, 768):
            pg = b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=1)
            pg.goto(URL, wait_until="load")
            pg.wait_for_timeout(1500)
            pg.eval_on_selector(".assure", "e=>e.scrollIntoView({block:'center'})")
            pg.wait_for_timeout(700)
            res[f"w{w}"] = measure(pg, f"w{w}", w)
            pg.close()
        b.close()
    print("ASSURE:" + json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
