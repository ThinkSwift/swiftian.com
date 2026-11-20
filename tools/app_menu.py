#!/usr/bin/env python3
"""app_menu.py — the app menu and the footer shared by all six sites
(RDM-web-app-menu-all-sites, -same-tab, -icons-only, RDM-web-one-footer).

Menu: four category labels with the 8 app icons under them; every app opens in the same tab; the
app's name is the icon's aria-label and tooltip. Icons are each app's own per-size files, never a
shrunk 1024. Footer: © line · the site's own extra links · Support · Privacy · email icon, in the
page's language (app-menu.js relabels it when a language toggle changes <html lang>).

    tools/app_menu.py                      # swiftian.com: rewrite menu + footer in its pages, and the
                                           # footer label table in assets/app-menu.js
    tools/app_menu.py --check              # exit 1 if anything above is out of date
    tools/app_menu.py --site coordigo.com  # another site's repo (~/Projects/<site>): menu, footer and
                                           # asset versions in every page that carries the menu
    tools/app_menu.py --site coordigo.com --check
    tools/app_menu.py --site coordigo.com --print        # head tags + menu block, for generators
    tools/app_menu.py --site coordigo.com --footer ko    # the footer block, for generators

On the other sites the CSS, the script and the icons load from https://swiftian.com, so one change
here reaches all six; bump CSS_V / JS_V when those files change. A light site sets the --am-*
colours (see the CSS); the footer keeps each site's own text and link colours.
"""

import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "swiftian.com"
SW = "https://swiftian.com"

# code, name, home site, path on that site, icon base (32/64/96 files), has 96, pixel art
APPS = {
    "EA": ("English Accents", "swiftian.com", "/ea/", "/assets/tabs/ea", True, True),
    "CP": ("Chinese Pronunciation", "swiftian.com", "/cp/", "/assets/tabs/cp", True, True),
    "SM": ("SeoulMal", "seoulmal.com", "/", "/assets/menu/sm", False, False),
    "MT": ("Times Tables & Multiplication", "swiftian.com", "/", "/assets/tabs/cf", True, True),
    "iF": ("iFlipbook", "iflipbook.com", "/", "/assets/menu/if", False, False),
    "Sp": ("Spriteer", "spriteer.com", "/", "/assets/menu/sp", False, True),
    "Co": ("Coordigo", "coordigo.com", "/", "/assets/tabs/site-coordigo", True, True),
    "Py": ("Pythoneer", "pythoneer.io", "/", "/assets/tabs/site-pythoneer", True, True),
}
GROUPS = [("Languages", ["EA", "CP", "SM"]), ("Math", ["MT"]),
          ("Art", ["iF", "Sp", "Co"]), ("Games", ["Py"])]

BEGIN, END = "<!-- app-menu -->", "<!-- /app-menu -->"


def icon(code):
    _, _, _, base, has96, px = APPS[code]
    src = f"{base}-32.png"
    srcset = f"{base}-32.png 1x, {base}-64.png 2x" + (f", {base}-96.png 3x" if has96 else "")
    if SITE != "swiftian.com":
        src, srcset = SW + src, ", ".join(SW + s.strip() for s in srcset.split(","))
    cls = ' class="px"' if px else ""
    return f'<img{cls} src="{src}" srcset="{srcset}" width="32" height="32" alt="">'


def link(code, cur, here):
    name, home, path, *_ = APPS[code]
    attrs = f' data-app="{code}"'
    if code == cur:
        return f'href="{here}" aria-current="page"{attrs}'
    if home == SITE:
        return f'href="{path}"{attrs}'
    src = SITE_APP.get(SITE, "sw").lower()
    url = f"https://{home}{path}?ct=web-{src}-menu"
    return f'href="{url}"{attrs}'


def name_attrs(code):
    # icons only on screen (founder 2026-11-08, RDM-web-app-menu-icons-only); the name stays for
    # screen readers and as the hover tooltip
    name = html.escape(APPS[code][0])
    return f' aria-label="{name}" title="{name}"'


def menu(cur, here):
    groups = "".join(
        f'<div class="am-g"><p class="am-h">{g}</p><div class="am-row">'
        + "".join(f'<a class="am-i" {link(c, cur, here)}{name_attrs(c)}>{icon(c)}</a>' for c in codes)
        + "</div></div>" for g, codes in GROUPS)
    return f'{BEGIN}<div class="am" role="navigation" aria-label="Swiftian apps"><div class="am-bar">{groups}</div></div>{END}'


def current(rel):
    if rel == "index.html":
        return "MT"
    if rel.startswith("cp/"):
        return "CP"
    return "EA"   # /ea/ and its language copies


OLD_TABS = re.compile(r'<div class="tabs">.*?</div>(?=\s*<button class="lang-toggle|\s*</nav>)', re.S)
BLOCK = re.compile(re.escape(BEGIN) + ".*?" + re.escape(END), re.S)
CSS_V, JS_V = 6, 2   # bump when app-menu.css / app-menu.js change; every page on all six sites follows
CSS = f'<link rel="stylesheet" href="/assets/app-menu.css?v={CSS_V}">'
JS = f'<script src="/assets/app-menu.js?v={JS_V}" defer></script>'


def rewrite(text, cur, here):
    new = menu(cur, here)
    if BEGIN in text:
        text = BLOCK.sub(lambda m: new, text, count=1)
    else:
        text, n = OLD_TABS.subn(lambda m: new, text, count=1)
        if not n:
            raise SystemExit("no tab bar found")
    if CSS not in text:
        text = re.sub(r'<link rel="stylesheet" href="/assets/app-menu\.css[^"]*">\n?', "", text)
        text = text.replace("</head>", f"{CSS}\n</head>", 1)
    if JS not in text:
        text = re.sub(r'<script src="/assets/app-menu\.js[^"]*" defer></script>\n?', "", text)
        text = text.replace("</body>", f"{JS}\n</body>", 1)
    return text


SITE_APP = {"seoulmal.com": "SM", "iflipbook.com": "iF", "spriteer.com": "Sp",
            "coordigo.com": "Co", "pythoneer.io": "Py"}


# ── One footer on all six sites (founder 2026-11-08, "통일하기": RDM-web-one-footer) ──
# © line · the site's own extra links · Support · Privacy · email icon, dots between, centred.
# Labels follow the page language; app-menu.js relabels them when a page's language toggle
# changes <html lang> (its table is written from LABELS below, so the two never drift).
FOOT_BEGIN, FOOT_END = "<!-- site-footer -->", "<!-- /site-footer -->"

# locale: (support, privacy, terms)
LABELS = {
    "en": ("Support", "Privacy", "Terms"),
    "ar": ("الدعم", "الخصوصية", "الشروط"),
    "de": ("Support", "Datenschutz", "Bedingungen"),
    "es": ("Soporte", "Privacidad", "Términos"),
    "es-mx": ("Soporte", "Privacidad", "Términos"),
    "fr": ("Assistance", "Confidentialité", "Conditions"),
    "hi": ("सहायता", "गोपनीयता", "शर्तें"),
    "id": ("Dukungan", "Privasi", "Ketentuan"),
    "it": ("Supporto", "Privacy", "Termini"),
    "ja": ("サポート", "プライバシー", "利用規約"),
    "ko": ("지원", "개인정보", "이용약관"),
    "nl": ("Support", "Privacy", "Voorwaarden"),
    "pt-br": ("Suporte", "Privacidade", "Termos"),
    "ru": ("Поддержка", "Конфиденциальность", "Условия"),
    "sv": ("Support", "Integritet", "Villkor"),
    "th": ("ฝ่ายสนับสนุน", "ความเป็นส่วนตัว", "ข้อกำหนด"),
    "tr": ("Destek", "Gizlilik", "Koşullar"),
    "vi": ("Hỗ trợ", "Quyền riêng tư", "Điều khoản"),
    "zh-hans": ("支持", "隐私", "条款"),
    "zh-hant": ("支援", "隱私權", "條款"),
}
# swiftian.com's language pages (the © line on the other sites links there in the page's language)
SW_LOCALES = {"ar", "de", "es", "fr", "hi", "id", "it", "ja", "ko", "pt-br", "ru", "th", "tr", "vi",
              "zh-hans", "zh-hant"}
# site: (name on the © line, extra links before Terms/Support/Privacy, has /terms/, has /support/)
FOOT_SITE = {
    "swiftian.com": ("Swiftian Inc.", [], False, False),
    "seoulmal.com": ("SeoulMal", [], False, True),
    "iflipbook.com": ("iFlipbook", [], False, True),
    "coordigo.com": ("Coordigo", [], False, True),
    "pythoneer.io": ("Pythoneer", [("https://www.youtube.com/@PythoneerIO", "YouTube")], True, False),
    "spriteer.com": ("Spriteer", [], False, True),
}
MAIL = ('<a class="mail email" data-u="hello" data-d="swiftian.com" href="#" aria-label="Email us" title="Email us">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/>'
        '<path d="m4 7 8 6 8-6"/></svg></a>')


def footer(site, loc="en"):
    loc = loc if loc in LABELS else "en"
    support, privacy, terms = LABELS[loc]
    name, extras, has_terms, has_support = FOOT_SITE[site]
    if site == "swiftian.com":
        first = f'<span class="sf-c">&copy; 2026 {name}</span>'
    else:
        sw = f"https://swiftian.com/{loc}/" if loc in SW_LOCALES else "https://swiftian.com/"
        first = f'<span class="sf-c">&copy; 2026 {name} &middot; <a href="{sw}">Swiftian Inc.</a></span>'
    items = [first] + [f'<a href="{u}">{html.escape(t)}</a>' for u, t in extras]
    if has_terms:
        items.append(f'<a href="/terms/" data-sf="terms">{terms}</a>')
    if has_support:
        items.append(f'<a href="/support/" data-sf="support">{support}</a>')
    items += [f'<a href="/privacy/" data-sf="privacy">{privacy}</a>', MAIL]
    # each link travels with the dot before it, so a phone's line break never strands a dot
    dot = '<span class="sf-dot" aria-hidden="true">&middot;</span>'
    rest = "".join(f'<span class="sf-x">{dot}{i}</span>' for i in items[1:])
    return f'{FOOT_BEGIN}<footer class="sf">{items[0]}{rest}</footer>{FOOT_END}'


def page_locale(rel):
    """The page's language from its path (/ko/…, /ea/ko/…); English otherwise."""
    for part in rel.split("/")[:-1]:
        if part in LABELS:
            return part
    return "en"


FOOTER_ANY = re.compile(r"[ \t]*<footer\b[^>]*>.*?</footer>", re.S)
FOOTER_BLOCK = re.compile(re.escape(FOOT_BEGIN) + ".*?" + re.escape(FOOT_END), re.S)
LANGS_NAV = re.compile(r'<nav class="langs".*?</nav>', re.S)


def put_footer(text, site, loc):
    """Swap the page's footer for the shared one. A language list that lived inside the old footer
    (iflipbook.com's language pages) stays, just above it."""
    new = footer(site, loc)
    if FOOT_BEGIN in text:
        return FOOTER_BLOCK.sub(lambda m: new, text, count=1)
    olds = list(FOOTER_ANY.finditer(text))
    if not olds:
        return text
    m = olds[-1]
    langs = LANGS_NAV.search(m.group(0))
    keep = f'<div class="container sf-langs">{langs.group(0)}</div>\n  ' if langs else ""
    return text[:m.start()] + "  " + keep + new + text[m.end():]


def js_labels():
    rows = ",".join(f'"{k}":{{support:"{s}",privacy:"{p}",terms:"{t}"}}' for k, (s, p, t) in LABELS.items())
    return "var SF = {" + rows + "};"


def print_site(site):
    global SITE
    SITE = site
    cur = SITE_APP[site]
    print(f'<link rel="stylesheet" href="{SW}/assets/app-menu.css?v={CSS_V}">')
    print(f'<script src="{SW}/assets/app-menu.js?v={JS_V}" defer></script>')
    print(menu(cur, "/"))


LANG_DIR = re.compile(r"[a-z]{2}(-[a-z]{2,4})?")


def write_site(site, check=False):
    """Another site's repo (~/Projects/<site>): every page that carries the menu gets the current
    menu (its own app current, linking to the language home or the site home), the shared footer
    in the page's language and the current asset versions. Returns (pages, changed)."""
    global SITE
    SITE = site
    root = os.path.expanduser(f"~/Projects/{site}")
    cur = SITE_APP[site]
    css = re.compile(r'https://swiftian\.com/assets/app-menu\.css\?v=\d+')
    js = re.compile(r'https://swiftian\.com/assets/app-menu\.js\?v=\d+')
    pages, changed = 0, []
    for d, _, files in os.walk(root):
        if "/.git" in d:
            continue
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(d, f)
            text = open(p, encoding="utf-8").read()
            if BEGIN not in text:
                continue
            pages += 1
            rel = os.path.relpath(p, root)
            first = rel.split("/")[0] if "/" in rel else ""
            here = f"/{first}/" if LANG_DIR.fullmatch(first) else "/"
            new = BLOCK.sub(lambda m: menu(cur, here), text, count=1)
            new = put_footer(new, site, page_locale(rel))
            new = css.sub(f"{SW}/assets/app-menu.css?v={CSS_V}", new)
            new = js.sub(f"{SW}/assets/app-menu.js?v={JS_V}", new)
            if new != text:
                changed.append(rel)
                if not check:
                    open(p, "w", encoding="utf-8").write(new)
    return pages, changed


JS_FILE = os.path.join(ROOT, "assets", "app-menu.js")
JS_TABLE = re.compile(r"  // footer labels \(tools/app_menu\.py\)\n.*?\n")


def write_js_labels(check=False):
    text = open(JS_FILE, encoding="utf-8").read()
    new = JS_TABLE.sub(lambda m: "  // footer labels (tools/app_menu.py)\n  " + js_labels() + "\n", text, count=1)
    if new != text and not check:
        open(JS_FILE, "w", encoding="utf-8").write(new)
    return new != text


def main():
    check = "--check" in sys.argv
    if "--site" in sys.argv:
        site = sys.argv[sys.argv.index("--site") + 1]
        if "--footer" in sys.argv:
            global SITE
            SITE = site
            print(footer(site, sys.argv[sys.argv.index("--footer") + 1]))
        elif "--print" in sys.argv:
            print_site(site)
        else:
            pages, changed = write_site(site, check)
            verb = "out of date" if check else "rewritten"
            print(f"{site}: {pages - len(changed)}/{pages} pages current, {len(changed)} {verb}")
            if check and changed:
                sys.exit(1)
        return
    if write_js_labels(check):
        print("assets/app-menu.js: footer labels " + ("out of date" if check else "rewritten"))
        if check:
            sys.exit(1)
    stale, done = [], 0
    for d, _, files in os.walk(ROOT):
        if ".git" in d or "/tools" in d:
            continue
        for f in files:
            if f != "index.html":
                continue
            p = os.path.join(d, f)
            rel = os.path.relpath(p, ROOT)
            text = open(p, encoding="utf-8").read()
            if 'class="tabs-bar' not in text:
                continue
            here = "/" + os.path.dirname(rel) + ("/" if os.path.dirname(rel) else "")
            new = put_footer(rewrite(text, current(rel), here), SITE, page_locale(rel))
            done += 1
            if new != text:
                stale.append(rel)
                if not check:
                    open(p, "w", encoding="utf-8").write(new)
    verb = "out of date" if check else "rewritten"
    print(f"app menu: {done - len(stale)}/{done} pages current, {len(stale)} {verb}")
    if check and stale:
        print("\n".join("  " + s for s in sorted(stale)))
        sys.exit(1)


if __name__ == "__main__":
    main()
