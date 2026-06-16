#!/usr/bin/env python3
"""Remove the baked-in checkerboard from the Mariah 'shoot me a text' image and
emit a clean transparent webp. Border flood-fill over light+desaturated pixels —
stops at the colored subject and the pink-outlined speech bubble."""
import sys
from collections import deque
from PIL import Image, ImageFilter

SRC = r"C:\Users\zacgi\Downloads\ChatGPT Image Jun 15, 2026, 11_30_51 PM.png"
OUT = r"C:\Users\zacgi\Gibson-Caretaker-Services\public\mariah-text.webp"
PREVIEW = r"C:\Users\zacgi\Gibson-Caretaker-Services\.shots\cutout_preview.png"

im = Image.open(SRC).convert("RGBA")
W, H = im.size
px = im.load()

def is_bg(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    return mx >= 216 and (mx - mn) <= 24   # light AND low-saturation = the gray/white checker

# BFS flood-fill from every border pixel
seen = bytearray(W * H)
dq = deque()
for x in range(W):
    dq.append((x, 0)); dq.append((x, H - 1))
for y in range(H):
    dq.append((0, y)); dq.append((W - 1, y))
removed = 0
while dq:
    x, y = dq.popleft()
    if x < 0 or y < 0 or x >= W or y >= H:
        continue
    i = y * W + x
    if seen[i]:
        continue
    seen[i] = 1
    r, g, b, a = px[x, y]
    if not is_bg(r, g, b):
        continue
    px[x, y] = (r, g, b, 0)
    removed += 1
    dq.append((x + 1, y)); dq.append((x - 1, y)); dq.append((x, y + 1)); dq.append((x, y - 1))
print("removed bg pixels:", removed, "of", W * H)

# Feather: erode the alpha by ~1px then slight blur, to kill the checker fringe halo
a = im.getchannel("A")
a = a.filter(ImageFilter.MinFilter(3))      # erode 1px into the subject
a = a.filter(ImageFilter.GaussianBlur(0.8))  # soft edge
im.putalpha(a)

# Trim to content bounding box
bbox = im.getbbox()
if bbox:
    im = im.crop(bbox)
    print("trimmed to", im.size)

# Resize to a sensible display size (~720px wide covers 2x DPR for a ~360px display)
maxw = 680
if im.width > maxw:
    im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)

im.save(OUT, "WEBP", quality=82, method=6)
import os
print("wrote", OUT, os.path.getsize(OUT), "bytes at", im.size)

# preview on a blush card so I can judge the edges
prev = Image.new("RGBA", (im.width + 120, im.height + 120), (251, 234, 241, 255))
prev.alpha_composite(im, (60, 60))
prev.convert("RGB").save(PREVIEW)
print("wrote preview", PREVIEW)
