#!/usr/bin/env python3
"""Build the production public/index.html from the verified concept:
- port the live <head> SEO/meta (incl. the Fraunces SOFT-axis font link)
- fix the four image paths ./x.webp -> /x.webp
- strip the CONCEPT comment, the concept tag, and the dead Facebook link
- back up the current live index.html, copy the new hydrangea asset
- allowlist cdnjs in the CSP, remove the stray loader-dev.html
Prints self-checks; does NOT deploy."""
import pathlib, re, shutil, sys

ROOT = pathlib.Path(r"C:\Users\zacgi\Gibson-Caretaker-Services")
LIVE = ROOT / "public" / "index.html"
PUB  = ROOT / "public" / "index.html"
CONCEPT = pathlib.Path(r"C:\Users\zacgi\Downloads\gcs-concept.html")
BACKUPS = ROOT / "backups"; BACKUPS.mkdir(exist_ok=True)

live = LIVE.read_text(encoding="utf-8").split("\n")
seo = "\n".join(live[14:42])                      # live lines 15-42: title -> SOFT-axis font link
assert "<title>" in seo and 'rel="stylesheet"' in seo and "og:image" in seo, "SEO block wrong"

html = CONCEPT.read_text(encoding="utf-8")

# 1) swap the concept head (title -> font link) for the live SEO block
start = html.index("<title>Gibson Caretaker Services — concept</title>")
end = html.index('rel="stylesheet" />', start) + len('rel="stylesheet" />')
html = html[:start] + seo + html[end:]

# 2) strip the CONCEPT comment + concept tag + Facebook dead link
html = re.sub(r"<!-- CONCEPT DEMO.*?-->\n?", "", html, flags=re.S)
html = re.sub(r'\s*<div class="concept-tag">.*?</div>', "", html, flags=re.S)
html = re.sub(r'\n\s*\.concept-tag\{[^}]*\}', "", html)                       # unused CSS
html = re.sub(r'\n\s*@media\(min-width:901px\)\{\.concept-tag\{bottom:14px\}\}', "", html)
html = re.sub(r'\s*<p class="fline"><a href="#"[^>]*>Find me on Facebook</a></p>', "", html)

# 3) fix the four real image paths (scoped, not a blind ./ replace)
for a, b in [("./mariah.webp", "/mariah.webp"), ("./mariah-text.webp", "/mariah-text.webp"),
             ("./gibson-hero.webp", "/gibson-hero.webp"), ("./gcs-after.webp", "/gcs-after.webp")]:
    html = html.replace(a, b)

# ---- self-checks ----
problems = []
if 'href="#"' in html: problems.append('dead href="#" remains')
if "concept-tag" in html: problems.append("concept tag/css remains")
if re.search(r'(src|href|url\()\s*["\']?\./', html): problems.append("a ./ relative path remains")
if "gibsoncaretakerservices.com/og.jpg" not in html: problems.append("og meta missing")
if "cdnjs.cloudflare.com/ajax/libs/gsap" not in html: problems.append("gsap script missing")
if 'SOFT,wght' not in html: problems.append("SOFT-axis font link missing")
for img in ["/mariah.webp", "/mariah-text.webp", "/gibson-hero.webp", "/gcs-after.webp"]:
    if img not in html: problems.append("missing img ref " + img)
if problems:
    print("SELF-CHECK FAILED:", problems); sys.exit(1)

# ---- write (backup first) ----
shutil.copy2(LIVE, BACKUPS / "index-pre-redesign-2026-06-17.html")
PUB.write_text(html, encoding="utf-8")

# new asset
shutil.copy2(pathlib.Path(r"C:\Users\zacgi\Downloads\gcs-after.webp"), ROOT / "public" / "gcs-after.webp")

# CSP: allowlist cdnjs for GSAP
hp = ROOT / "public" / "_headers"
h = hp.read_text(encoding="utf-8")
old = "script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com https://challenges.cloudflare.com"
new = old + " https://cdnjs.cloudflare.com"
assert old in h, "CSP script-src not found as expected"
hp.write_text(h.replace(old, new), encoding="utf-8")

# remove stray dev artifact
dev = ROOT / "public" / "loader-dev.html"
if dev.exists(): dev.unlink()

print("OK -> public/index.html (%d bytes); backup saved; gcs-after.webp copied; CSP +cdnjs; loader-dev removed" % len(html))
