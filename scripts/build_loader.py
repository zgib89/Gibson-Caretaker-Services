#!/usr/bin/env python3
"""Transform the embed loader (gcs-loader-EMBED.html) with the site-integration mods,
and emit a standalone dev page for visual tuning. A second pass injects into index.html."""
import re, io, sys

EMBED = r"C:\Users\zacgi\Downloads\gibson-caretaker-loading-screen\gcs-loader-EMBED.html"
DEV   = r"C:\Users\zacgi\Gibson-Caretaker-Services\public\loader-dev.html"

src = io.open(EMBED, encoding="utf-8").read()

def repl(old, new, label):
    global src
    n = src.count(old)
    if n != 1:
        print(f"  !! [{label}] expected 1 match, got {n}")
        return
    src = src.replace(old, new)
    print(f"  ok [{label}]")

# MOD-1: background -> the site's blush (white+rose fading to #fbf4f3 base)
repl("  background:radial-gradient(135% 105% at 50% 36%, #FFF1F7 0%, #FBE0EC 46%, #F3C7DC 78%, #EAB6CF 100%);",
     "  background:#fbf4f3 radial-gradient(125% 108% at 50% 28%, #fff7fc 0%, #ffe7f2 36%, #fbe6ef 64%, #fbf4f3 100%);",
     "blush background")

# MOD-2: external webp instead of 147KB inline base64
src = re.sub(r'url\("data:image/webp;base64,[^"]*"\)', 'url("./gibson-hero.webp")', src)
src = src.replace("background:#F8D6E3 url", "background:#fbeaf1 url")
print("  ok [external webp url]")

# MOD-3: stage — drop the card frame, fade edges into bg, gentle entrance (no webp pop)
repl("  width:min(100%, calc(100vh * 1.7768), 1640px);",
     "  width:min(86%, calc(80vh * 1.7768), 1480px);",
     "frame the scene in blush (desktop margin)")
repl("  border-radius:18px;overflow:hidden;",
     "  overflow:hidden;\n"
     "  -webkit-mask-image:radial-gradient(116% 128% at 50% 48%, #000 46%, rgba(0,0,0,0) 100%);\n"
     "  mask-image:radial-gradient(116% 128% at 50% 48%, #000 46%, rgba(0,0,0,0) 100%);",
     "edge-fade mask (drop border-radius)")
repl("  box-shadow:0 40px 80px -34px rgba(124,40,87,.55), 0 0 0 1px rgba(255,255,255,.35) inset;\n",
     "", "drop card box-shadow")
repl("  animation:gcs-breathe 10s ease-in-out infinite;\n  will-change:transform;",
     "  animation:gcs-breathe 10s ease-in-out infinite, gcs-stage-in 1.3s cubic-bezier(.2,.8,.2,1) both;\n  will-change:transform,opacity;",
     "stage entrance animation")
repl(".gcs-scene{display:block;width:100%;height:100%}",
     ".gcs-scene{display:block;width:100%;height:100%}\n"
     "/* mobile: scale the landscape scene up to fill portrait; edge-fade mask hides the overflow */\n"
     "@media (max-aspect-ratio: 4/5){ .gcs-stage{ width:min(170%, calc(100vh * 0.95)); } }\n"
     "@keyframes gcs-stage-in{ from{opacity:0;transform:translate3d(0,10px,0) scale(.985)} to{opacity:1} }",
     "mobile scale + stage-in keyframe")

# MOD-4: petals FALL (top -> down) to match the site's signature
repl(".gcs-petal{position:absolute;bottom:-8%;opacity:0;will-change:transform,opacity;",
     ".gcs-petal{position:absolute;top:-8%;opacity:0;will-change:transform,opacity;",
     "petals start above")
repl("""@keyframes gcs-drift{
  0%{opacity:0;transform:translate3d(0,0,0) rotate(0)}
  8%{opacity:var(--op,.85)}
  50%{transform:translate3d(26px,-54vh,0) rotate(180deg)}
  90%{opacity:var(--op,.85)}
  100%{opacity:0;transform:translate3d(-18px,-112vh,0) rotate(360deg)}}""",
"""@keyframes gcs-drift{
  0%{opacity:0;transform:translate3d(0,0,0) rotate(0)}
  8%{opacity:var(--op,.85)}
  50%{transform:translate3d(26px,54vh,0) rotate(160deg)}
  90%{opacity:var(--op,.85)}
  100%{opacity:0;transform:translate3d(-18px,112vh,0) rotate(320deg)}}""",
     "petals drift downward")

# MOD-6: animate fully for everyone (owner preference: motion-on for this site)
repl("""@media (prefers-reduced-motion: reduce){
  /* keep the localized water + the progress fill; drop only the big motion */
  .gcs-stage{animation:none!important}
  .gcs-petal{display:none!important}
}""",
     "/* loader animates fully for everyone (owner-directed: motion-on for this site) */",
     "remove RM degradation (CSS)")
repl("""      var reduce = false;
      try { reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}""",
     "      var reduce = false; /* loader plays fully for everyone (owner preference) */",
     "force full motion (JS)")

# MOD-4b: petal palette -> light blush-rose to match the site's falling petals
repl("      var COLORS = ['#E85FA0', '#C9276A', '#B79CE6', '#F2785C', '#FFFFFF', '#F49ABF'];",
     "      var COLORS = ['#ffc2d8', '#ffd6e6', '#ffe4f0', '#ffffff', '#fbb8d0', '#f7a6c4'];",
     "blush petal palette")

# MOD-5: announce the fade start so the site can play the wordmark in crossfade
repl("        L.classList.add('gcs-done');",
     "        L.classList.add('gcs-done');\n        try { window.dispatchEvent(new Event('gcs:fading')); } catch (e) {}",
     "dispatch gcs:fading")

# ---- emit standalone dev page ----
css   = re.search(r'<style id="gcs-loader-css">.*?</style>', src, re.S).group(0)
mk    = re.search(r'<div id="gcs-loader".*?</div>\s*</div>\s*</div>', src, re.S)
# markup spans from <div id="gcs-loader"> to its matching close — grab to just before the script
markup = src[src.index('<div id="gcs-loader"'):src.index('<script id="gcs-loader-js"')].strip()
js    = re.search(r'<script id="gcs-loader-js">.*?</script>', src, re.S).group(0)

dev = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
       '<title>loader dev</title>'
       '<style>html,body{margin:0;height:100%;background:#fbf4f3;font-family:Georgia,serif}'
       '.behind{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;'
       'font-size:42px;color:#bf1568}</style></head><body>'
       '<div class="behind">Gibson Caretaker Services</div>'
       + css + "\n" + markup + "\n" + js +
       '</body></html>')
io.open(DEV, "w", encoding="utf-8", newline="").write(dev)
print("wrote dev page:", DEV, "(", len(dev), "bytes )")

# ---- inject into index.html ----
if "--inject" in sys.argv:
    INDEX = r"C:\Users\zacgi\Gibson-Caretaker-Services\public\index.html"
    idx = io.open(INDEX, encoding="utf-8").read()
    if 'id="gcs-loader"' in idx:
        print("INJECT: loader already present — skipping.")
    else:
        css_i = css.replace("./gibson-hero.webp", "/gibson-hero.webp")
        markup_i = markup.replace("./gibson-hero.webp", "/gibson-hero.webp")
        js_i = js
        preload = '<link rel="preload" as="image" href="/gibson-hero.webp" />\n'
        cloak = '<style>.wm-cloak{opacity:0;transition:opacity .7s ease}</style>\n'
        assert idx.count("</head>") >= 1 and idx.count("<body data-season=\"summer\">") == 1
        idx = idx.replace("</head>", preload + css_i + "\n" + cloak + "</head>", 1)
        idx = idx.replace('<body data-season="summer">',
                          '<body data-season="summer">\n' + markup_i + "\n" + js_i, 1)
        OLD = "  playIntro();window.addEventListener('pageshow',function(e){if(e.persisted)playIntro();});"
        NEW = (
"  // Loader handoff: cloak the wordmark, then play its intro AS the loader dissolves (no snap-back).\n"
"  (function(){\n"
"    var WM=$('.wordmark');\n"
"    function reveal(){ if(!WM) return; WM.classList.remove('wm-cloak'); playIntro(); }\n"
"    function arm(){\n"
"      if(WM) WM.classList.add('wm-cloak');\n"
"      var fired=false; function go(){ if(fired)return; fired=true; reveal(); }\n"
"      window.addEventListener('gcs:fading', function(){ setTimeout(go,280); }, {once:true});\n"
"      window.addEventListener('gcs:revealed', go, {once:true});\n"
"      setTimeout(go, 11000);\n"
"    }\n"
"    if(document.getElementById('gcs-loader')) arm(); else playIntro();\n"
"    window.addEventListener('pageshow', function(e){\n"
"      if(!e.persisted) return;\n"
"      if(window.__gcsReplay){ arm(); window.__gcsReplay(); } else playIntro();\n"
"    });\n"
"  })();"
        )
        if OLD in idx:
            idx = idx.replace(OLD, NEW, 1)
            print("INJECT: wordmark handoff wired.")
        else:
            print("!! INJECT: playIntro anchor NOT found — handoff NOT wired.")
        io.open(INDEX, "w", encoding="utf-8", newline="").write(idx)
        print("INJECT: wrote index.html (", len(idx), "bytes )")
