#!/usr/bin/env python3
"""Reduced-motion regression check: scene must paint a static frame and the
season switcher must still swap it; no console errors."""
import sys, json, io, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

TARGET = pathlib.Path(sys.argv[1]).resolve().as_uri()
def arr(b): return np.asarray(Image.open(io.BytesIO(b)).convert("RGB"), dtype=np.int16)
def diff(a, b): return float(np.abs(a-b).mean()/255*100) if a.shape == b.shape else 100.0

def main():
    r = {"console_errors": []}
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        ctx = br.new_context(viewport={"width": 390, "height": 844},
                             device_scale_factor=2, reduced_motion="reduce")
        pg = ctx.new_page()
        pg.on("console", lambda m: r["console_errors"].append(m.text) if m.type == "error" else None)
        pg.goto(TARGET, wait_until="load")
        pg.wait_for_timeout(1200)
        scene = pg.locator("#scene")
        a = arr(scene.screenshot())
        r["scene_nonblank_RM"] = bool(a.std() > 8)
        # static: two shots 400ms apart should be ~identical (no animation under RM)
        s1 = arr(scene.screenshot()); pg.wait_for_timeout(400); s2 = arr(scene.screenshot())
        r["static_drift_RM_pct"] = round(diff(s1, s2), 4)
        r["is_static_RM"] = bool(diff(s1, s2) < 0.05)
        # season switch still repaints under RM
        b = arr(scene.screenshot())
        pg.locator('.seasons button[data-season="winter"]').click()
        pg.wait_for_timeout(400)
        c = arr(scene.screenshot())
        r["winter_pressed_RM"] = pg.get_attribute('.seasons button[data-season="winter"]', "aria-pressed")
        r["season_switch_repaint_RM_pct"] = round(diff(b, c), 4)
        r["season_switch_ok_RM"] = bool(diff(b, c) > 0.5 and r["winter_pressed_RM"] == "true")
        br.close()
    print("RM:" + json.dumps(r))

if __name__ == "__main__":
    main()
