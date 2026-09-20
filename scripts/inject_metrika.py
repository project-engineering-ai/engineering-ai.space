#!/usr/bin/env python3
"""Idempotent Yandex.Metrika + geo-lang injector, runs in CI before Pages deploy.

Inserts into every HTML file under ROOT that misses them:
  1) the Metrika counter block,
  2) the contact_click reachGoal listener,
  3) the geo-localization script tag (skipped for excluded files, e.g. 404.html:
     a language redirect there would replace an honest 404 with the homepage).

This makes both the tracking and the language routing survive any future
static-site regeneration committed to the repo.

Usage: python3 scripts/inject_metrika.py --cid 112548629 --root . [--dry-run]
"""
import argparse
import pathlib
import sys

METRIKA_TMPL = """<!-- Yandex.Metrika counter -->
<script type="text/javascript" >
   (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
   m[i].l=1*new Date();
   for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
   k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
   (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");

   ym(__CID__, "init", {
        clickmap:false,
        trackLinks:true,
        accurateTrackBounce:true,
        webvisor:true
   });
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/__CID__" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->
"""

LISTENER_TMPL = (
    '<script>document.addEventListener("click",function(e){'
    "var a=e.target&&e.target.closest?e.target.closest('a[href^=\\\\\\\"mailto:\\\\\\\"],a[href^=\\\\\\\"tel:\\\\\\\"]'):null;"
    'if(a&&window.ym){try{ym(__CID__,"reachGoal","contact_click");}catch(_){}}'
    '},true);</script>'
)

GEO_TAG = '<script defer src="/geo-lang.js"></script>'

# Эти файлы не получают редирект по языку (служебные/верификационные).
GEO_EXCLUDE = ("404.html",)


def inject(html: str, cid: int, geo_ok: bool = True):
    changed = False
    cid = str(cid)
    if "mc.yandex.ru/watch" not in html:
        block = METRIKA_TMPL.replace("__CID__", cid)
    else:
        block = ""
    listener = LISTENER_TMPL.replace("__CID__", cid)
    need_listener = "contact_click" not in html and "</head>" in html
    need_geo = geo_ok and "geo-lang.js" not in html and "</head>" in html
    if need_geo:
        block += GEO_TAG + "\n"
        changed = True

    if not block and not need_listener:
        return html, False

    if "</head>" in html:
        html = html.replace("</head>", (block + (listener + "\n" if need_listener else "")) + "</head>", 1)
        changed = True
    elif block:
        # no head (feed-ish or fragment) — prepend
        html = block + html
        changed = True
    return html, changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cid", type=int, required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    files = sorted(root.rglob("*.html"))
    touched = 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        new, changed = inject(text, args.cid, geo_ok=not any(f.match(p) for p in GEO_EXCLUDE))
        if changed:
            touched += 1
            print(("DRY " if args.dry_run else "INJECT ") + str(f))
            if not args.dry_run:
                f.write_text(new, encoding="utf-8", newline="")
    print(f"scanned={len(files)} injected={touched}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
