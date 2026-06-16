#!/usr/bin/env python3
"""Per-viewport legibility stress-test for the fixed aurora background.
For each dark-text-on-light spot: scroll it into view, make text transparent
(layout unchanged), screenshot the VIEWPORT (captures the fixed aura behind it),
sample the composite background across the text box, compute WCAG contrast vs the
text's true color. Pass = every spot >= 4.5 (AA). Usage: verify_bg.py <url|path> [w]"""
import sys, io, json, pathlib, re
from playwright.sync_api import sync_playwright
from PIL import Image

arg = sys.argv[1]
URL = arg if arg.startswith("http") else pathlib.Path(arg).resolve().as_uri()
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1280

SEL = ["h1", ".lead", ".hero-tip", ".hero-copy .eyebrow", ".how h2",
       "section.act-light .act-head h2", "section.act-light .a-lede",
       "section.act-light .item b", "section.act-light .item span",
       ".gardener .bio", ".gardener h2", ".faq h2", ".faq-cta",
       ".assure-item b", ".assure-item>span:last-child", ".price-lead"]


def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(p):
    return 0.2126 * lin(p[0]) + 0.7152 * lin(p[1]) + 0.0722 * lin(p[2])


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def rgb(s):
    n = [int(x) for x in re.findall(r"\d+", s)[:3]]
    return tuple(n) if len(n) == 3 else (0, 0, 0)


def main():
    out = {"url": URL, "w": W, "spots": []}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": W, "height": 900}, device_scale_factor=1)
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(1400)
        pg.add_style_tag(content=".rv{opacity:1!important;transform:none!important}")
        # read colors first
        cols = pg.evaluate("""(sels)=>{const o={};for(const s of sels){const e=document.querySelector(s);if(e)o[s]=getComputedStyle(e).color;}return o;}""", SEL)
        # make text transparent (keep layout)
        pg.add_style_tag(content="*{color:transparent!important;text-shadow:none!important;-webkit-text-fill-color:transparent!important}")
        worst = (99.0, None)
        for s in SEL:
            if s not in cols:
                continue
            try:
                pg.locator(s).first.scroll_into_view_if_needed(timeout=2500)
            except Exception:
                continue
            pg.wait_for_timeout(250)
            r = pg.evaluate("""(s)=>{const e=document.querySelector(s);const b=e.getBoundingClientRect();return {x:b.left,y:b.top,w:b.width,h:b.height};}""", s)
            shot = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
            tc = rgb(cols[s])
            mn = 99.0
            for fx in (0.04, 0.25, 0.5, 0.75, 0.96):
                x = int(min(max(r["x"] + r["w"] * fx, 0), shot.width - 1))
                y = int(min(max(r["y"] + r["h"] * 0.5, 0), shot.height - 1))
                mn = min(mn, contrast(tc, shot.getpixel((x, y))))
            out["spots"].append({"sel": s, "text": list(tc), "min_contrast": round(mn, 2)})
            if mn < worst[0]:
                worst = (mn, s)
        out["worst"] = {"sel": worst[1], "contrast": round(worst[0], 2)}
        out["all_pass_AA"] = bool(worst[0] >= 4.5)
        b.close()
    print("BG:" + json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
