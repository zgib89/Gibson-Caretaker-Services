#!/usr/bin/env python3
"""
Verification harness for the seasonal-scene canvas + general no-regression checks.

Loads public/index.html via file:// in headless Chromium and asserts:
  1. No console errors / page errors.
  2. The hero #scene canvas actually renders (non-uniform pixels).
  3. The season switcher works (clicking Winter sets aria-pressed + repaints).
  4. The booking form is present.
  5. DIFFERENTIAL RESIZE TEST (the reported scroll-jump bug):
       - diff_natural   = how much the scene changes over ~320ms with NO resize (particle drift).
       - diff_noop_resize = how much it changes over ~320ms when a no-op window 'resize'
         is dispatched (mobile URL-bar scroll simulation; viewport size unchanged).
     With the bug, a no-op resize rebuilds the scene -> all flora teleport -> diff_noop_resize
     is many times diff_natural. When fixed, diff_noop_resize ~= diff_natural.
  6. REAL RESIZE still re-fits: changing the viewport height changes the canvas backing store.

Usage:  python verify_scene.py <path-to-index.html>
Outputs a JSON blob of metrics on the last line (prefixed RESULT:).
"""
import sys, json, io, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

_arg = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\zacgi\Gibson-Caretaker-Services\public\index.html"
URL = _arg if _arg.startswith("http") else pathlib.Path(_arg).resolve().as_uri()


def arr(png_bytes):
    return np.asarray(Image.open(io.BytesIO(png_bytes)).convert("RGB"), dtype=np.int16)


def mean_abs_diff_pct(a, b):
    if a.shape != b.shape:
        return 100.0
    return float(np.abs(a - b).mean() / 255.0 * 100.0)


def shot(locator):
    return arr(locator.screenshot())


def main():
    res = {"url": URL, "console_errors": [], "page_errors": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 844},
                                device_scale_factor=2)
        page.on("console", lambda m: res["console_errors"].append(m.text)
                if m.type == "error" else None)
        page.on("pageerror", lambda e: res["page_errors"].append(str(e)))

        page.goto(URL, wait_until="load")
        page.wait_for_timeout(1600)  # let fonts + scene spin up

        scene = page.locator("#scene")
        res["scene_present"] = scene.count() > 0

        # (2) non-blank: stddev of pixels across the canvas
        a0 = shot(scene)
        res["scene_pixel_stddev"] = float(a0.std())
        res["scene_nonblank"] = bool(a0.std() > 8)

        # (4) form present
        res["form_present"] = page.locator("#bookForm").count() > 0
        res["daypicker_filled"] = page.locator("#daypick .chip").count() >= 10

        # (5a) natural drift baseline (no resize), ~320ms
        n1 = shot(scene)
        page.wait_for_timeout(320)
        n2 = shot(scene)
        res["diff_natural_pct"] = round(mean_abs_diff_pct(n1, n2), 4)

        # (5b) no-op resize (simulate mobile URL-bar fire; viewport unchanged), ~320ms
        r1 = shot(scene)
        page.evaluate("() => window.dispatchEvent(new Event('resize'))")
        page.wait_for_timeout(320)  # past the 180ms debounce
        r2 = shot(scene)
        res["diff_noop_resize_pct"] = round(mean_abs_diff_pct(r1, r2), 4)

        ratio = (res["diff_noop_resize_pct"] / res["diff_natural_pct"]
                 if res["diff_natural_pct"] > 0.0001 else 999.0)
        res["resize_vs_natural_ratio"] = round(ratio, 2)
        # Heuristic verdict: a no-op resize should not move the scene much more than nature does.
        res["scroll_jump_present"] = bool(ratio > 3.0 and res["diff_noop_resize_pct"] > 1.0)

        # (3) season switch: click Winter, expect aria-pressed + a repaint
        before = shot(scene)
        page.locator('.seasons button[data-season="winter"]').click()
        page.wait_for_timeout(900)
        after = shot(scene)
        res["winter_aria_pressed"] = page.locator(
            '.seasons button[data-season="winter"]').get_attribute("aria-pressed") == "true"
        res["season_switch_repaint_pct"] = round(mean_abs_diff_pct(before, after), 4)
        res["season_switch_ok"] = bool(res["winter_aria_pressed"]
                                       and res["season_switch_repaint_pct"] > 0.5)

        # (6) real resize re-fits the backing store
        w_before = page.evaluate("() => document.querySelector('#scene').width")
        page.set_viewport_size({"width": 390, "height": 600})
        page.wait_for_timeout(350)
        w_after_h = page.evaluate("() => document.querySelector('#scene').height")
        page.set_viewport_size({"width": 720, "height": 800})
        page.wait_for_timeout(350)
        w_after_w = page.evaluate("() => document.querySelector('#scene').width")
        res["real_resize_width_changed"] = bool(w_after_w != w_before)
        res["scene_width_before"] = w_before
        res["scene_width_after_wide"] = w_after_w

        browser.close()

    print("RESULT:" + json.dumps(res))


if __name__ == "__main__":
    main()
