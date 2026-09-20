#!/usr/bin/env python3
"""Идемпотентный инжектор гео-локализации для статических сайтов.

Добавляет в каждый .html под --root:
  1) <script defer src="/geo-lang.js"></script> перед </head> (если ещё нет);
  2) атрибут data-lang-switch="force" на переключатель языка, если он размечен
     простым <li><a href="en/|/"></a></li> (статические HTML-страницы).

Скрипт можно безопасно запускать повторно и в CI: он не дублирует теги.

Usage:
  python3 scripts/inject_geolang.py --root _site [--script /geo-lang.js] [--dry-run]
"""
import argparse
import pathlib
import re
import sys

TAG_TMPL = '<script defer src="__SRC__"></script>'

# Переключатель языка в статической вёрстке: <li><a href="en/" ...>EN</a></li>
# Текст ссылки (EN/RU/ENGLISH/РУС) — надёжный признак переключателя, поэтому href
# может быть любым (en/, /, en/about.html, ...).
SWITCH_RE = re.compile(
    r'(<li><a href="[^"]*"(?![^>]*data-lang-switch)[^>]*>'
    r'(?:EN|RU|ENGLISH|РУС)</a></li>)'
)

# Служебные HTML-файлы: их трогать нельзя (верификация поисковиков, 404).
DEFAULT_EXCLUDE = ("404.html", "yandex_*.html", "google*.html", "yandex*.html")


def inject(html: str, src: str) -> tuple:
    changed = False
    if "geo-lang.js" not in html:
        tag = TAG_TMPL.replace("__SRC__", src)
        if "</head>" in html:
            html = html.replace("</head>", tag + "\n</head>", 1)
            changed = True
        elif "<body" in html:
            html = html.replace("<body", tag + "\n<body", 1)
            changed = True
    if "data-lang-switch" not in html:
        new, n = SWITCH_RE.subn(
            lambda m: m.group(1).replace("<a ", '<a data-lang-switch="force" ', 1), html)
        if n:
            html = new
            changed = True
    return html, changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--script", default="/geo-lang.js")
    ap.add_argument("--exclude", default=",".join(DEFAULT_EXCLUDE),
                    help="glob-паттерны имён файлов, которые не трогаем")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    patterns = [p.strip() for p in args.exclude.split(",") if p.strip()]
    files = [f for f in sorted(root.rglob("*.html"))
             if not any(f.match(p) for p in patterns)]
    skipped = len(sorted(root.rglob("*.html"))) - len(files)
    touched = 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        new, changed = inject(text, args.script)
        if changed:
            touched += 1
            print(("DRY " if args.dry_run else "INJECT ") + str(f))
            if not args.dry_run:
                f.write_text(new, encoding="utf-8", newline="")
    print(f"scanned={len(files)} injected={touched} skipped={skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
