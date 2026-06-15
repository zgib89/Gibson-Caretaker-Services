#!/usr/bin/env python3
"""Extra checks not in verify_scene: form-error focus/aria-invalid, season-card canvases,
and a no-op-resize stability check on a season card."""
import sys, json, io, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

TARGET = pathlib.Path(sys.argv[1]).resolve().as_uri()


def arr(b): return np.asarray(Image.open(io.BytesIO(b)).convert("RGB"), dtype=np.int16)
def diff(a, b): return float(np.abs(a - b).mean() / 255.0 * 100.0) if a.shape == b.shape else 100.0


def main():
    r = {"console_errors": []}
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        pg = br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg.on("console", lambda m: r["console_errors"].append(m.text) if m.type == "error" else None)
        pg.goto(TARGET, wait_until="load")
        pg.wait_for_timeout(1400)

        # --- season cards present + render ---
        r["season_card_count"] = pg.locator("canvas[data-card]").count()
        pg.locator('section.act[aria-labelledby="summer-h"]').scroll_into_view_if_needed()
        pg.wait_for_timeout(900)
        card = pg.locator('canvas[data-card="summer"]')
        c1 = arr(card.screenshot())
        r["summer_card_nonblank"] = bool(c1.std() > 8)
        # no-op resize must not teleport the card either
        s1 = arr(card.screenshot()); pg.wait_for_timeout(300); s2 = arr(card.screenshot())
        nat = diff(s1, s2)
        rs1 = arr(card.screenshot()); pg.evaluate("()=>window.dispatchEvent(new Event('resize'))")
        pg.wait_for_timeout(300); rs2 = arr(card.screenshot())
        rz = diff(rs1, rs2)
        r["card_natural_pct"] = round(nat, 3); r["card_noop_resize_pct"] = round(rz, 3)
        r["card_jump_present"] = bool(nat > 0.0001 and rz / max(nat, 0.0001) > 3.0 and rz > 1.0)

        # --- form error: submit empty -> focus moves to #name, aria-invalid set, specific msg ---
        pg.locator("#bookForm").scroll_into_view_if_needed()
        pg.wait_for_timeout(400)
        pg.evaluate("()=>document.getElementById('send').click()")
        pg.wait_for_timeout(300)
        r["focused_id_after_empty_submit"] = pg.evaluate("()=>document.activeElement && document.activeElement.id")
        r["name_aria_invalid"] = pg.get_attribute("#name", "aria-invalid")
        r["status_text"] = (pg.inner_text("#status") or "")[:80]

        # fill name only, submit -> should now flag phone and focus phone
        pg.fill("#name", "Test Person")
        pg.evaluate("()=>document.getElementById('send').click()")
        pg.wait_for_timeout(300)
        r["focused_id_after_name_only"] = pg.evaluate("()=>document.activeElement && document.activeElement.id")
        r["phone_aria_invalid"] = pg.get_attribute("#phone", "aria-invalid")

        br.close()
    print("EXTRA:" + json.dumps(r))


if __name__ == "__main__":
    main()
