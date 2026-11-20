#!/usr/bin/env python3
"""app_menu.py — the Swiftian bar, the Kawa Friends tabs and the one footer, on every site
(founder 2026-11-15, RDM-web-swiftian-app-kawafriends-family; replaces the 8-app category menu of
RDM-web-app-menu-all-sites; footer RDM-web-one-footer).

Bar: one ink strip at the very top of every page on every site, right after <body>: the eagle
(swiftian.com — the Swiftian app) on the left, the houses on the right: Kawa Friends · Pythoneer,
Spriteer · iFlipbook, Coordigo. Icons only (name = aria-label + tooltip), same tab, each icon the
app's own per-size file. seoulmal.com belongs to the Kawa Friends house, so its bar marks KF.
Tabs: the Kawa Friends house — Kawa Friends, Times Tables (Mu), English Accents, Chinese
Pronunciation, Seoul Mal — on kawafriends.com and seoulmal.com, between <!-- kf-tabs --> markers.
Footer: © line · the site's extra links · Support · Privacy · email icon, in the page's language
(bar.js relabels it when a language toggle changes <html lang>).

    tools/app_menu.py                      # swiftian.com
    tools/app_menu.py --check              # exit 1 if anything is out of date
    tools/app_menu.py --site coordigo.com  # another site's repo (~/Projects/<site>): bar, tabs,
                                           # footer and asset versions on every page that has the bar
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
    "Py": ("Pythoneer", "https://pythoneer.io/", "/assets/tabs/site-pythoneer", (32, 64, 96), True),
    "Sp": ("Spriteer", "https://spriteer.com/", "/assets/menu/sp", (32, 64), True),
    "iF": ("iFlipbook", "https://iflipbook.com/", "/assets/menu/if", (32, 64), False),
    "Co": ("Coordigo", "https://coordigo.com/", "/assets/tabs/site-coordigo", (32, 64, 96), True),
    # the Kawa Friends house
    "Mu": ("Multiplication & Times Tables", "https://kawafriends.com/mu/", "/assets/tabs/mu", (32, 64, 128), False),
    # Mu = the app's own icon files, byte for byte (founder 2026-11-20: the pixel panda left the web)
    "EA": ("English Accents", "https://kawafriends.com/ea/", "/assets/tabs/ea", (32, 64, 96), True),
    "CP": ("Chinese Pronunciation", "https://kawafriends.com/cp/", "/assets/tabs/cp", (32, 64, 96), True),
    "SM": ("Seoul Mal", "https://seoulmal.com/", "/assets/menu/sm", (32, 64), False),
}
BAR_GROUPS = [["KF"], ["Py", "Sp"], ["iF", "Co"]]
# the Kawa Friends tabs: code, label on wide screens, label on phones
TABS = [("KF", "Kawa Friends", "Friends"), ("Mu", "Times Tables", "Math"),
        ("EA", "English Accents", "English"), ("CP", "Chinese Pronunciation", "Chinese"),
        ("SM", "Seoul Mal", "Korean")]
# which bar icon is "here" on each site
SITE_HOUSE = {"swiftian.com": "SW", "kawafriends.com": "KF", "seoulmal.com": "KF", "pythoneer.io": "Py",
              "spriteer.com": "Sp", "iflipbook.com": "iF", "coordigo.com": "Co"}

BEGIN, END = "<!-- app-menu -->", "<!-- /app-menu -->"
TABS_BEGIN, TABS_END = "<!-- kf-tabs -->", "<!-- /kf-tabs -->"
CSS_V, JS_V = 1, 1   # bump when bar.css / bar.js change; every page on every site follows


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


def href(code, here):
    return local_path(code) or APPS[code][1]


def bar(here="/"):
    cur = SITE_HOUSE[SITE]

    def a(code, extra=""):
        name = html.escape(APPS[code][0])
        h = here if (code == cur and local_path(code) is not None) else href(code, here)
        currentness = ' aria-current="page"' if code == cur else ""
        return (f'<a class="sb-i{extra}" href="{h}"{currentness} data-app="{code}" aria-label="{name}" '
                f'title="{name}">{icon(code)}</a>')

    groups = '<i class="sb-d" aria-hidden="true"></i>'.join(
        '<div class="sb-g">' + "".join(a(c) for c in g) + "</div>" for g in BAR_GROUPS)
    return (f'{BEGIN}<div class="sb" role="navigation" aria-label="Swiftian"><div class="sb-in">'
            f'{a("SW", " sb-home")}<span class="sb-sp"></span>{groups}</div></div>{END}')


def tabs(cur, here):
    out = []
    for code, wide, short in TABS:
        name = html.escape(APPS[code][0])
        h = here if code == cur else href(code, here)
        currentness = ' aria-current="page"' if code == cur else ""
        out.append(f'<a class="kt-t" href="{h}"{currentness} data-app="{code}" title="{name}">{icon(code)}'
                   f'<span class="kt-l">{html.escape(wide)}</span><span class="kt-s" aria-hidden="true">{html.escape(short)}</span></a>')
    return (f'{TABS_BEGIN}<div class="kt" role="navigation" aria-label="Kawa Friends"><div class="kt-row">'
            + "".join(out) + f"</div></div>{TABS_END}")


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
    "seoulmal.com": ("Seoul Mal", [], False, True),
    "iflipbook.com": ("iFlipbook", [], False, True),
    "coordigo.com": ("Coordigo", [], False, True),
    "pythoneer.io": ("Pythoneer", [("https://www.youtube.com/@PythoneerIO", "YouTube")], True, False),
    "spriteer.com": ("Spriteer", [], False, True),
}
MAIL = ('<a class="mail email" data-u="hello" data-d="swiftian.com" href="#" aria-label="Email us" title="Email us">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/>'
        '<path d="m4 7 8 6 8-6"/></svg></a>')


# kawafriends.com carries four apps that live in the store under Swiftian Inc.'s privacy policy:
# their pages name their own app and link that policy (path prefix: name, privacy URL)
KF_PAGES = {"/mu/": ("Multiplication & Times Tables", SW + "/privacy/"),
            "/ea/": ("English Accents", SW + "/privacy/"),
            "/cp/": ("Chinese Pronunciation", SW + "/privacy/")}


def footer(site, loc="en", rel=""):
    loc = loc if loc in LABELS else "en"
    support, privacy, terms = LABELS[loc]
    name, extras, has_terms, has_support = FOOT_SITE[site]
    privacy_url = "/privacy/"
    if site == "kawafriends.com":
        for prefix, (n, pu) in KF_PAGES.items():
            if ("/" + rel).startswith(prefix):
                name, privacy_url, has_support = n, pu, False
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
TABS_BLOCK = re.compile(re.escape(TABS_BEGIN) + ".*?" + re.escape(TABS_END), re.S)
FOOTER_BLOCK = re.compile(re.escape(FOOT_BEGIN) + ".*?" + re.escape(FOOT_END), re.S)
BODY = re.compile(r"<body\b[^>]*>\n?")
OLD_CSS = re.compile(r'<link rel="stylesheet" href="(?:https?://[^"/]+)?/assets/(?:app-menu|bar)\.css[^"]*">\n?')
OLD_JS = re.compile(r'<script src="(?:https?://[^"/]+)?/assets/(?:app-menu|bar)\.js[^"]*" defer></script>\n?')
LANG_DIR = re.compile(r"[a-z]{2}(-[a-z]{2,4})?")


def head_tags():
    return (f'<link rel="stylesheet" href="{asset("/assets/bar.css")}?v={CSS_V}">',
            f'<script src="{asset("/assets/bar.js")}?v={JS_V}" defer></script>')


def rewrite(text, rel):
    """Bar right after <body>, tabs (where the page has the markers), footer, asset versions."""
    first = rel.split("/")[0] if "/" in rel else ""
    here = f"/{first}/" if (LANG_DIR.fullmatch(first) and SITE != "kawafriends.com") else "/"
    text = BLOCK.sub("", text)
    m = BODY.search(text)
    text = text[:m.end()] + bar(here) + "\n" + text[m.end():]
    if TABS_BEGIN in text:
        cur, tab_here = tab_state(rel)
        text = TABS_BLOCK.sub(lambda _m: tabs(cur, tab_here), text, count=1)
    if FOOT_BEGIN in text:
        text = FOOTER_BLOCK.sub(lambda _m: footer(SITE, page_locale(rel), rel), text, count=1)
    css, js = head_tags()
    text = OLD_CSS.sub("", text)
    text = OLD_JS.sub("", text)
    text = text.replace("</head>", f"{css}\n{js}\n</head>", 1)
    return text


def tab_state(rel):
    """(current tab, its own href) for a page on kawafriends.com or seoulmal.com."""
    d = "/" + os.path.dirname(rel) + "/" if os.path.dirname(rel) else "/"
    if SITE == "seoulmal.com":
        first = rel.split("/")[0] if "/" in rel else ""
        return "SM", (f"/{first}/" if LANG_DIR.fullmatch(first) else "/")
    for code, prefix in (("Mu", "/mu/"), ("EA", "/ea/"), ("CP", "/cp/")):
        if d.startswith(prefix):
            return code, (d if code == "EA" else prefix)
    return "KF", "/"


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
        print(bar("/"))
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
