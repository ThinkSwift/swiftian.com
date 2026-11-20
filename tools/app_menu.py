#!/usr/bin/env python3
"""app_menu.py — the Swiftian bar and the one footer, on every site
(bar: founder 2026-11-20, RDM-web-bar-families; footer RDM-web-one-footer).

Bar: one ink strip at the very top of every page on every site, right after <body>.
Left: the eagle alone (swiftian.com, the Swiftian app); no wordmark and no "/ <app>" crumb, the page
body already names itself (founder 2026-11-20).
Right: the apps, under the category labels people read at a glance (founder 2026-11-20: "languages,
art, math 이런식 분류"):
    [ Kawa Friends:  LANGUAGES  EA CP SM  ·  MATH  Mu ]   ART  iF Co Sp   GAMES  Py
The Kawa Friends apps sit together in one family pill that starts with the Kawa Friends icon (a family
of apps); iFlipbook, Spriteer, Pythoneer and Coordigo stand alone (one app, one site). Icons only
(name = aria-label + tooltip), same tab, every app one click from every page. Labels hide on narrow
screens, the family pill and dividers stay. Mu, EA (+ its language pages) and CP live on swiftian.com
until the Kawa Friends move (RDM-web-reframe-after-swiftian-app).
Footer: © line · the site's extra links · Support · Privacy · email icon, in the page's language
(bar.js relabels it when a language toggle changes <html lang>).

    tools/app_menu.py                      # swiftian.com
    tools/app_menu.py --check              # exit 1 if anything is out of date
    tools/app_menu.py --site coordigo.com  # another site's repo (~/Projects/<site>): bar, footer and
                                           # asset versions on every page that has the bar
    tools/app_menu.py --site coordigo.com --check
    tools/app_menu.py --site coordigo.com --print        # head tags + bar block, for generators
    tools/app_menu.py --site coordigo.com --footer ko    # the footer block, for generators

The bar block keeps the old marker names (<!-- app-menu -->) so generators that copy it keep
working; wherever a page has it, this tool moves it to just after <body>. The CSS, the script and
the icons load from https://swiftian.com, so one change here reaches every site; bump CSS_V / JS_V
when those files change.
"""

import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SW = os.environ.get("SW_ORIGIN", "https://swiftian.com")   # a local preview sets SW_ORIGIN
SITE = "swiftian.com"

# code: (name, url, icon base on swiftian.com, sizes drawn, pixel art)
APPS = {
    "SW": ("Swiftian", "https://swiftian.com/", "/assets/bar/sw", (32, 64, 96), True),
    "KF": ("Kawa Friends", "https://kawafriends.com/", "/assets/bar/kf", (32, 64), False),
    "EA": ("English Accents", "https://swiftian.com/ea/", "/assets/tabs/ea", (32, 64, 96), True),
    "CP": ("Chinese Pronunciation", "https://swiftian.com/cp/", "/assets/tabs/cp", (32, 64, 96), True),
    "SM": ("SeoulMal", "https://seoulmal.com/", "/assets/menu/sm", (32, 64, 96), True),
    # Mu = the red panda's face, close up, from the founder's crop (2026-11-20). A smooth drawing,
    # not pixel art: px False. Files keep the old cf- names.
    "Mu": ("Multiplication & Times Tables", "https://swiftian.com/mu/", "/assets/tabs/cf", (32, 64, 96), False),
    "iF": ("iFlipbook", "https://iflipbook.com/", "/assets/menu/if", (32, 64), False),
    "Sp": ("Spriteer", "https://spriteer.com/", "/assets/menu/sp", (32, 64), True),
    "Py": ("Pythoneer", "https://pythoneer.io/", "/assets/tabs/site-pythoneer", (32, 64, 96), True),
    "Co": ("CoordiGo", "https://coordigo.com/", "/assets/tabs/site-coordigo", (32, 64, 96), True),
}
# the Kawa Friends family: its head, then its categories
FAMILY = ("KF", [("Languages", ["EA", "CP", "SM"]), ("Math", ["Mu"])])
# the apps that stand alone, by category (Co back in Art next to iF, founder 2026-11-20)
SINGLES = [("Art", ["iF", "Co", "Sp"]), ("Games", ["Py"])]
SITE_APP = {"swiftian.com": "SW", "kawafriends.com": "KF", "seoulmal.com": "SM", "pythoneer.io": "Py",
            "spriteer.com": "Sp", "iflipbook.com": "iF", "coordigo.com": "Co"}
SW_DIRS = {"mu": "Mu", "race": "Mu", "defend": "Mu", "ea": "EA", "cp": "CP"}   # swiftian.com's app pages

BEGIN, END = "<!-- app-menu -->", "<!-- /app-menu -->"
CSS_V, JS_V = 3, 2   # bump when bar.css / bar.js change; every page on every site follows


def asset(path):
    return path if SITE == "swiftian.com" else SW + path


def icon(code):
    _, _, base, sizes, px = APPS[code]
    srcset = ", ".join(f"{asset(f'{base}-{s}.png')} {s // 32}x" for s in sizes)
    cls = ' class="px"' if px else ""
    return f'<img{cls} src="{asset(base + "-32.png")}" srcset="{srcset}" width="32" height="32" alt="">'


def local_path(code):
    """The app's URL as a path when it lives on this site, else None."""
    url = APPS[code][1]
    host = re.match(r"https://([^/]+)(/.*)", url)
    return host.group(2) if host.group(1) == SITE else None


def href(code):
    return local_path(code) or APPS[code][1]


def where(rel):
    """(current app, the href its icon keeps on this page) for a page at rel."""
    first = rel.split("/")[0] if "/" in rel else ""
    if SITE == "swiftian.com":
        if first in SW_DIRS:
            cur = SW_DIRS[first]
            return cur, (f"/{first}/" if cur != "Mu" else "/mu/")
        if first in LABELS:            # English Accents in another language
            return "EA", f"/{first}/"
        return "SW", "/"
    return SITE_APP[SITE], (f"/{first}/" if first in LABELS else "/")


def bar(rel="index.html"):
    cur, here = where(rel)

    def a(code, extra=""):
        name = html.escape(APPS[code][0])
        h = here if code == cur else href(code)
        currentness = ' aria-current="page"' if code == cur else ""
        return (f'<a class="sb-i{extra}" href="{h}"{currentness} data-app="{code}" aria-label="{name}" '
                f'title="{name}">{icon(code)}</a>')

    def cat(label, codes):
        return (f'<div class="sb-c"><span class="sb-l" aria-hidden="true">{label}</span>'
                + "".join(a(c) for c in codes) + "</div>")

    head, cats = FAMILY
    family = (f'<div class="sb-f" role="group" aria-label="Kawa Friends">{a(head, " sb-fh")}'
              '<i class="sb-fd" aria-hidden="true"></i>' + "".join(cat(l, c) for l, c in cats) + "</div>")
    singles = "".join('<i class="sb-d" aria-hidden="true"></i>' + cat(l, c) for l, c in SINGLES)
    home_h = here if cur == "SW" else href("SW")
    home_cur = ' aria-current="page"' if cur == "SW" else ""
    return (f'{BEGIN}<div class="sb" role="navigation" aria-label="Swiftian"><div class="sb-in">'
            f'<a class="sb-home" href="{home_h}"{home_cur} data-app="SW" aria-label="Swiftian" title="Swiftian">'
            f'{icon("SW")}</a>'
            f'<span class="sb-sp"></span><div class="sb-apps">{family}{singles}</div></div></div>{END}')


# ── one footer ──
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
# site: (name on the © line, extra links, has /terms/, has /support/)
FOOT_SITE = {
    "swiftian.com": ("Swiftian Inc.", [], False, False),
    "kawafriends.com": ("Kawa Friends", [], False, True),
    "seoulmal.com": ("SeoulMal", [], False, True),
    "iflipbook.com": ("iFlipbook", [], False, True),
    "coordigo.com": ("CoordiGo", [], False, True),
    "pythoneer.io": ("Pythoneer", [("https://www.youtube.com/@PythoneerIO", "YouTube")], True, False),
    "spriteer.com": ("Spriteer", [], False, True),
}
MAIL = ('<a class="mail email" data-u="hello" data-d="swiftian.com" href="#" aria-label="Email us" title="Email us">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/>'
        '<path d="m4 7 8 6 8-6"/></svg></a>')



def footer(site, loc="en", rel=""):
    loc = loc if loc in LABELS else "en"
    support, privacy, terms = LABELS[loc]
    name, extras, has_terms, has_support = FOOT_SITE[site]
    privacy_url = "/privacy/"
    if site == "swiftian.com":
        first = f'<span class="sf-c">&copy; 2026 {html.escape(name)}</span>'
    else:
        first = f'<span class="sf-c">&copy; 2026 {html.escape(name)} &middot; <a href="{SW}/">Swiftian Inc.</a></span>'
    items = [first] + [f'<a href="{u}">{html.escape(t)}</a>' for u, t in extras]
    if has_terms:
        items.append(f'<a href="/terms/" data-sf="terms">{terms}</a>')
    if has_support:
        items.append(f'<a href="/support/" data-sf="support">{support}</a>')
    items += [f'<a href="{privacy_url}" data-sf="privacy">{privacy}</a>', MAIL]
    dot = '<span class="sf-dot" aria-hidden="true">&middot;</span>'
    rest = "".join(f'<span class="sf-x">{dot}{i}</span>' for i in items[1:])
    return f'{FOOT_BEGIN}<footer class="sf">{items[0]}{rest}</footer>{FOOT_END}'


def page_locale(rel):
    for part in rel.split("/")[:-1]:
        if part in LABELS:
            return part
    return "en"


BLOCK = re.compile(r"[ \t]*" + re.escape(BEGIN) + ".*?" + re.escape(END) + r"\n?", re.S)
FOOTER_BLOCK = re.compile(re.escape(FOOT_BEGIN) + ".*?" + re.escape(FOOT_END), re.S)
BODY = re.compile(r"<body\b[^>]*>\n?")
OLD_CSS = re.compile(r'<link rel="stylesheet" href="(?:https?://[^"/]+)?/assets/(?:app-menu|bar)\.css[^"]*">\n?')
OLD_JS = re.compile(r'<script src="(?:https?://[^"/]+)?/assets/(?:app-menu|bar)\.js[^"]*" defer></script>\n?')


def head_tags():
    return (f'<link rel="stylesheet" href="{asset("/assets/bar.css")}?v={CSS_V}">',
            f'<script src="{asset("/assets/bar.js")}?v={JS_V}" defer></script>')


def rewrite(text, rel):
    """Bar right after <body>, footer, asset versions."""
    text = BLOCK.sub("", text)
    m = BODY.search(text)
    text = text[:m.end()] + bar(rel) + "\n" + text[m.end():]
    if FOOT_BEGIN in text:
        text = FOOTER_BLOCK.sub(lambda _m: footer(SITE, page_locale(rel), rel), text, count=1)
    css, js = head_tags()
    text = OLD_CSS.sub("", text)
    text = OLD_JS.sub("", text)
    text = text.replace("</head>", f"{css}\n{js}\n</head>", 1)
    return text


def run(site, check=False):
    global SITE
    SITE = site
    root = ROOT if site == "swiftian.com" else os.path.expanduser(f"~/Projects/{site}")
    pages, changed = 0, []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in {".git", "tools", "node_modules", "_drafts"}]
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(d, f)
            text = open(p, encoding="utf-8").read()
            if BEGIN not in text:
                continue
            pages += 1
            rel = os.path.relpath(p, root)
            new = rewrite(text, rel)
            if new != text:
                changed.append(rel)
                if not check:
                    open(p, "w", encoding="utf-8").write(new)
    return pages, changed


JS_FILE = os.path.join(ROOT, "assets", "bar.js")
JS_TABLE = re.compile(r"  // footer labels \(tools/app_menu\.py\)\n.*?\n")


def js_labels():
    rows = ",".join(f'"{k}":{{support:"{s}",privacy:"{p}",terms:"{t}"}}' for k, (s, p, t) in LABELS.items())
    return "var SF = {" + rows + "};"


def write_js_labels(check=False):
    text = open(JS_FILE, encoding="utf-8").read()
    new = JS_TABLE.sub(lambda m: "  // footer labels (tools/app_menu.py)\n  " + js_labels() + "\n", text, count=1)
    if new != text and not check:
        open(JS_FILE, "w", encoding="utf-8").write(new)
    return new != text


def main():
    global SITE
    check = "--check" in sys.argv
    site = sys.argv[sys.argv.index("--site") + 1] if "--site" in sys.argv else "swiftian.com"
    SITE = site
    if "--footer" in sys.argv:
        print(footer(site, sys.argv[sys.argv.index("--footer") + 1]))
        return
    if "--print" in sys.argv:
        css, js = head_tags()
        print(css)
        print(js)
        print(bar())
        return
    if site == "swiftian.com" and write_js_labels(check):
        print("assets/bar.js: footer labels " + ("out of date" if check else "rewritten"))
        if check:
            sys.exit(1)
    pages, changed = run(site, check)
    verb = "out of date" if check else "rewritten"
    print(f"{site}: {pages - len(changed)}/{pages} pages current, {len(changed)} {verb}")
    if check and changed:
        print("\n".join("  " + s for s in sorted(changed)))
        sys.exit(1)


if __name__ == "__main__":
    main()
