#!/usr/bin/env python3
"""Production QA sweep for the live site."""
import sys, json
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "https://gibsoncaretakerservices.com/"


def main():
    out = {"url": URL, "console_errors": [], "page_errors": []}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.on("console", lambda m: out["console_errors"].append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: out["page_errors"].append(str(e)))
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(2000)
        # links
        links = pg.eval_on_selector_all("a[href]", "els=>els.map(e=>e.getAttribute('href'))")
        ids = set(pg.eval_on_selector_all("[id]", "els=>els.map(e=>e.id)"))
        tel = [l for l in links if l.startswith("tel:")]
        sms = [l for l in links if l.startswith("sms:")]
        mailto = [l for l in links if l.startswith("mailto:")]
        ext = [l for l in links if l.startswith("http")]
        anchors = [l for l in links if l.startswith("#")]
        bad_anchors = [a for a in anchors if a != "#" and a[1:] not in ids]
        out["tel_unique"] = sorted(set(tel))
        out["sms_count"] = len(sms)
        out["mailto_unique"] = sorted(set(mailto))
        out["external_unique"] = sorted(set(ext))
        out["broken_internal_anchors"] = bad_anchors
        # phone/email consistency
        out["all_tel_match"] = all("16083417826" in t for t in tel)
        out["facebook_present"] = any("facebook.com" in e for e in ext)
        out["mariah_email_leak"] = pg.evaluate("()=>document.body.innerText.includes('mariah@')")
        out["real_phone_visible"] = pg.evaluate("()=>document.body.innerText.includes('341-7826')")
        out["gmail_visible"] = pg.evaluate("()=>document.body.innerText.includes('gibsoncaretakerservices@gmail.com')")
        # images broken?
        out["broken_images"] = pg.eval_on_selector_all("img", "els=>els.filter(e=>e.complete&&e.naturalWidth===0).length")
        out["img_count"] = pg.eval_on_selector_all("img", "els=>els.length")
        out["img_missing_alt"] = pg.eval_on_selector_all("img", "els=>els.filter(e=>!e.hasAttribute('alt')).length")
        # form
        out["form_present"] = pg.locator("#bookForm").count() == 1
        out["form_required"] = pg.eval_on_selector_all("#bookForm [required]", "els=>els.map(e=>e.id)")
        out["daypicker_days"] = pg.locator("#daypick .chip").count()
        # headings order
        out["h1_count"] = pg.locator("h1").count()
        # title + meta
        out["title"] = pg.title()
        out["has_description"] = pg.locator('meta[name=description]').count() == 1
        out["has_canonical"] = pg.locator('link[rel=canonical]').count() == 1
        out["has_og_image"] = pg.locator('meta[property="og:image"]').count() == 1
        # JSON-LD valid?
        lds = pg.eval_on_selector_all('script[type="application/ld+json"]', "els=>els.map(e=>e.textContent)")
        valid = 0
        for s in lds:
            try:
                json.loads(s); valid += 1
            except Exception:
                pass
        out["jsonld_blocks"] = len(lds); out["jsonld_valid"] = valid
        # aurora + petals present
        out["aura_petals"] = pg.locator(".aura .petal").count()
        b.close()
    print("QA:" + json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
