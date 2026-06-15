#!/usr/bin/env python3
"""Desktop behavior check: do hero + cards ANIMATE (drift), does the season
switcher change the hero scene, and what happens under reduced-motion.
Usage: python desktop_anim.py <url-or-path> [width]"""
import sys, json, io, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

arg = sys.argv[1]
URL = arg if arg.startswith("http") else pathlib.Path(arg).resolve().as_uri()
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1280


def a(b): return np.asarray(Image.open(io.BytesIO(b)).convert("RGB"), dtype=np.int16)
def diff(x, y): return float(np.abs(x - y).mean() / 255 * 100) if x.shape == y.shape else 100.0


def run(reduced):
    r = {"reduced_motion": reduced, "console_errors": []}
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        ctx = br.new_context(viewport={"width": W, "height": 900}, device_scale_factor=1,
                             reduced_motion=("reduce" if reduced else "no-preference"))
        pg = ctx.new_page()
        pg.on("console", lambda m: r["console_errors"].append(m.text) if m.type == "error" else None)
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(1500)

        # hero animation drift (hero is in view at top)
        hero = pg.locator("#scene")
        h1 = a(hero.screenshot()); pg.wait_for_timeout(500); h2 = a(hero.screenshot())
        r["hero_anim_drift_pct"] = round(diff(h1, h2), 4)
        r["hero_animates"] = bool(diff(h1, h2) > 0.3)

        # season switch on hero (desktop)
        b1 = a(hero.screenshot())
        pg.locator('.seasons button[data-season="winter"]').click()
        pg.wait_for_timeout(900)
        b2 = a(hero.screenshot())
        r["hero_season_switch_pct"] = round(diff(b1, b2), 4)
        r["hero_season_switch_ok"] = bool(diff(b1, b2) > 0.5)

        # a season card: scroll in, check animation drift
        card = pg.locator('canvas[data-card="summer"]')
        card.scroll_into_view_if_needed()
        pg.wait_for_timeout(800)
        c1 = a(card.screenshot()); pg.wait_for_timeout(500); c2 = a(card.screenshot())
        r["card_anim_drift_pct"] = round(diff(c1, c2), 4)
        r["card_animates"] = bool(diff(c1, c2) > 0.3)
        br.close()
    return r


def main():
    print("ANIM:" + json.dumps([run(False), run(True)], indent=1))


if __name__ == "__main__":
    main()
