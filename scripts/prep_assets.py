#!/usr/bin/env python3
"""Concept assets: confirm cutout dims (diagnose stretch) + optimize the real
hydrangea garden photo into a web webp for the iMessage after-photo mock."""
from PIL import Image
import pathlib
dl = pathlib.Path(r"C:\Users\zacgi\Downloads")

ct = Image.open(dl / "mariah-text.webp")
print("mariah-text.webp size:", ct.size, "ratio w/h:", round(ct.size[0]/ct.size[1], 3))

src = dl / "pexels-soc-nang-d-ng-2150345854-34109197.jpg"
im = Image.open(src).convert("RGB")
print("hydrangea orig:", im.size)
w = 1000
h = round(im.size[1] * w / im.size[0])
im2 = im.resize((w, h), Image.LANCZOS)
out = dl / "gcs-after.webp"
im2.save(out, "WEBP", quality=84, method=6)
print("saved:", out.name, im2.size, "ratio:", round(w/h, 3), out.stat().st_size, "bytes")
