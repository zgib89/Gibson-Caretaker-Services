#!/usr/bin/env python3
"""Desktop-viewport canvas render check. For each canvas (hero + 4 season cards):
report CSS box size, backing-store size, and pixel stddev (blank if ~0), after
scrolling it into view. Usage: python desktop_check.py <url-or-path> [width]"""
import sys, json, io, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

arg = sys.argv[1]
URL = arg if arg.startswith("http") else pathlib.Path(arg).resolve().as_uri()
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1280


def stddev(b):
    return float(np.asarray(Image.open(io.BytesIO(b)).convert("RGB")).std())


def main():
    out = {"url": URL, "viewport_w": W, "console_errors": [], "canvases": []}
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        pg = br.new_page(viewport={"width": W, "height": 900}, device_scale_factor=1)
        pg.on("console", lambda m: out["console_errors"].append(m.text) if m.type == "error" else None)
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(1600)

        sels = ["#scene", 'canvas[data-card="spring"]', 'canvas[data-card="summer"]',
                'canvas[data-card="autumn"]', 'canvas[data-card="winter"]']
        for sel in sels:
            loc = pg.locator(sel)
            if loc.count() == 0:
                out["canvases"].append({"sel": sel, "present": False})
                continue
            loc.scroll_into_view_if_needed()
            pg.wait_for_timeout(700)
            dims = pg.evaluate(
                "(s)=>{const c=document.querySelector(s);const r=c.getBoundingClientRect();"
                "return {cssW:Math.round(r.width),cssH:Math.round(r.height),bw:c.width,bh:c.height};}", sel)
            sd = stddev(loc.screenshot())
            out["canvases"].append({"sel": sel, "present": True, **dims,
                                    "stddev": round(sd, 2), "blank": bool(sd < 6)})
        br.close()
    print("DESKTOP:" + json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
