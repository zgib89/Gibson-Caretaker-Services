#!/usr/bin/env python3
"""Extract the inline base64 portrait from index.html into an optimized public/mariah.webp,
then replace the data-URI <img> with a cacheable lazy-loaded reference.
Center-crops to square to match the existing object-fit:cover display (no visual change)."""
import re, base64, io
from PIL import Image

HTML = r"C:\Users\zacgi\Gibson-Caretaker-Services\public\index.html"
WEBP = r"C:\Users\zacgi\Gibson-Caretaker-Services\public\mariah.webp"

src = io.open(HTML, encoding="utf-8").read()

m = re.search(r'<img decoding="async" src="data:image/jpeg;base64,([^"]+)"([^>]*)>', src)
if not m:
    raise SystemExit("portrait <img> not found")

b64 = m.group(1)
rest = m.group(2)
alt_m = re.search(r'alt="([^"]*)"', rest)
alt = alt_m.group(1) if alt_m else "Mariah Gibson, smiling and holding a bright bouquet of flowers"
print("existing alt:", alt[:80])

raw = base64.b64decode(b64)
print("inline base64 bytes:", len(b64), "-> decoded jpeg bytes:", len(raw))

im = Image.open(io.BytesIO(raw)).convert("RGB")
w, h = im.size
print("source dims:", w, "x", h)

# center-crop to square (matches the .portrait aspect-ratio:1 + object-fit:cover display)
side = min(w, h)
left = (w - side) // 2
top = (h - side) // 2
im = im.crop((left, top, left + side, top + side))

# cap at 720 (display ~360px @2x DPR); never upscale
target = min(720, side)
if side != target:
    im = im.resize((target, target), Image.LANCZOS)

im.save(WEBP, "WEBP", quality=82, method=6)
import os
print("wrote mariah.webp:", os.path.getsize(WEBP), "bytes at", target, "x", target)

new_img = (f'<img src="/mariah.webp" width="{target}" height="{target}" '
           f'alt="{alt}" loading="lazy" decoding="async">')
src = src[:m.start()] + new_img + src[m.end():]
io.open(HTML, "w", encoding="utf-8", newline="").write(src)
print("replaced inline data-URI <img> with /mariah.webp reference")
print("index.html now:", os.path.getsize(HTML), "bytes (was ~230KB)")
