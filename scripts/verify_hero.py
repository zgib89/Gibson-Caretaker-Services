#!/usr/bin/env python3
"""Above-fold measurement + success-state + h1-color snapshot."""
import sys, json, pathlib
from playwright.sync_api import sync_playwright

URL = pathlib.Path(sys.argv[1]).resolve().as_uri()

def main():
    r = {}
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        pg = br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(1400)
        VH = 844
        def top(sel):
            return pg.evaluate(f"() => {{const e=document.querySelector('{sel}'); return e? Math.round(e.getBoundingClientRect().top):null;}}")
        r["h1_top"] = top("h1")
        r["lead_top"] = top(".lead")
        r["first_cta_top"] = top(".hero-cta .btn")
        r["h1_visible_above_fold"] = bool(r["h1_top"] is not None and r["h1_top"] < VH)
        r["first_cta_above_fold"] = bool(r["first_cta_top"] is not None and r["first_cta_top"] < VH)
        r["lead_text"] = (pg.inner_text(".lead") or "")[:200]
        r["h1_em_color"] = pg.evaluate("() => getComputedStyle(document.querySelector('.hero-copy h1 em')).color")
        # crop hero for visual judgment
        pg.screenshot(path=".shots/v2_hero_mobile.png", clip={"x":0,"y":0,"width":390,"height":844})
        # success state: inject ok class and screenshot the status
        pg.locator("#bookForm").scroll_into_view_if_needed()
        pg.evaluate("()=>{const s=document.getElementById('status'); s.className='status ok'; s.textContent='Thank you - your request is on its way to Mariah. She will reach out soon to confirm.';}")
        pg.wait_for_timeout(200)
        pg.locator("#status").screenshot(path=".shots/v2_success.png")
        r["success_bg"] = pg.evaluate("()=>getComputedStyle(document.getElementById('status')).backgroundColor")
        br.close()
    print("HERO:" + json.dumps(r))

if __name__ == "__main__":
    main()
