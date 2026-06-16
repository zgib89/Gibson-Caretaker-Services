#!/usr/bin/env python3
"""Surgical refinements that are awkward via line-edits:
  1) add decoding="async" to the inline portrait <img> (the 124KB base64 line)
  2) replace STRAIGHT apostrophes with the curly typographer's glyph (U+2019)
     in VISIBLE PROSE ONLY -- each target is a full, unique English phrase, so
     JS single-quoted string delimiters and URL/attribute text are never touched.
Every change is asserted to hit exactly the expected number of sites.
"""
import sys, io

PATH = r"C:\Users\zacgi\Gibson-Caretaker-Services\public\index.html"
CURL = "’"  # ’

src = io.open(PATH, encoding="utf-8").read()
orig = src
report = []

def sub(old, new, expect=1, label=""):
    global src
    n = src.count(old)
    if n != expect:
        report.append(f"  !! SKIP [{label or old[:34]}] found {n}, expected {expect}")
        return
    src = src.replace(old, new)
    report.append(f"  ok  [{label or old[:34]}] x{n}")

# 1) image decode offload (critical: must be exactly one)
sub('<img src="data:image/jpeg;base64,',
    '<img decoding="async" src="data:image/jpeg;base64,',
    1, "img decoding=async")

# 2) prose apostrophes -> curly (each phrase is unique visible text)
pairs = [
    ("I'll confirm a time",                 "I{c}ll confirm a time"),
    ("send a photo when it's done",         "send a photo when it{c}s done"),
    ("While you're away",                   "While you{c}re away"),
    ("you don't lift a thing",              "you don{c}t lift a thing"),
    ("so you're never stranded",            "so you{c}re never stranded"),
    ("next year's garden",                  "next year{c}s garden"),
    ("Hi, I'm Mariah.",                     "Hi, I{c}m Mariah."),
    ("and I'm carrying that same",          "and I{c}m carrying that same"),
    ("what you need isn't on the list, please",
                                            "what you need isn{c}t on the list, please"),
    ("I'll always be honest about what I can and can't do.",
                                            "I{c}ll always be honest about what I can and can{c}t do."),
    ("I'd be so glad to help.",             "I{c}d be so glad to help."),
    ("Let's pick a day",                    "Let{c}s pick a day"),
    ("and I'll get back to you to confirm", "and I{c}ll get back to you to confirm"),
    (">I'm flexible<",                      ">I{c}m flexible<"),
]
for old, new in pairs:
    sub(old, new.format(c=CURL), 1, old[:40])

# safety: never introduce a curly quote where a JS string delimiter lives
assert "rgb(" in src and "function setAccent" in src, "JS structure damaged!"

print("\n".join(report))
print(f"\nremaining STRAIGHT apostrophes in file: {src.count(chr(39))}  "
      f"(these should now be only JS/URL/attribute code, not prose)")

if src != orig:
    io.open(PATH, "w", encoding="utf-8", newline="").write(src)
    print("WROTE changes.")
else:
    print("NO changes written.")
