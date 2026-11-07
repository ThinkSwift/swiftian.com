#!/usr/bin/env python3
"""app_menu.py — write the one app menu into a site's pages (RDM-web-app-menu-all-sites, RDM-web-app-menu-marks).

The 8 apps are the buttons, under four category labels. Apps on the site being written open in
the same tab; apps on another site open it in a new tab and show its domain under the name
(EA, CP and MT live on swiftian.com and never show a domain). Icons are each app's own
per-size files (32 px and 2x), never a shrunk 1024.

    tools/app_menu.py                 # swiftian.com: rewrite the menu in every page that has one
    tools/app_menu.py --check         # exit 1 if any page's menu is out of date
    tools/app_menu.py --site coordigo.com --print
                                      # the other five sites: print the head tags and the menu block
                                      # for that site (its own app current, its home as the link);
                                      # their pages and generators carry it between the markers

On the other sites the CSS, the click script and the icons load from https://swiftian.com, so
one change here reaches all six. A site whose page is light sets the --am-* colours (see the CSS).

The menu sits inside <nav class="tabs-bar"> between the markers below; the page's language
toggle (if any) stays in the nav. Styles: /assets/app-menu.css, clicks: /assets/app-menu.js.
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


def label(code):
    name, home, *_ = APPS[code]
    dom = f'<span class="am-d">{home}</span>' if home != SITE and home != "swiftian.com" else ""
    return f'<span class="am-n">{html.escape(name)}{dom}</span>'


def menu(cur, here):
    bar = "".join(
        f'<div class="am-g"><p class="am-h">{g}</p><div class="am-row">'
        + "".join(f'<a class="am-b" {link(c, cur, here)}>{icon(c)}{label(c)}</a>' for c in codes)
        + "</div></div>" for g, codes in GROUPS)
    rows = "".join(
        f'<p class="am-h">{g}</p>'
        + "".join(f'<a class="am-r" {link(c, cur, here)}>{icon(c)}{label(c)}</a>' for c in codes)
        for g, codes in GROUPS)
    summary = f'<summary>{icon(cur)}<span class="am-n">{html.escape(APPS[cur][0])}</span><span class="am-more">8 apps</span></summary>'
    return (f'{BEGIN}<div class="am"><div class="am-bar">{bar}</div>'
            f'<details class="am-m">{summary}<div class="am-list">{rows}</div></details></div>{END}')


def current(rel):
    if rel == "index.html":
        return "MT"
    if rel.startswith("cp/"):
        return "CP"
    return "EA"   # /ea/ and its language copies


OLD_TABS = re.compile(r'<div class="tabs">.*?</div>(?=\s*<button class="lang-toggle|\s*</nav>)', re.S)
BLOCK = re.compile(re.escape(BEGIN) + ".*?" + re.escape(END), re.S)
CSS = '<link rel="stylesheet" href="/assets/app-menu.css?v=2">'
JS = '<script src="/assets/app-menu.js?v=1" defer></script>'


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


def print_site(site):
    global SITE
    SITE = site
    cur = SITE_APP[site]
    print(f'<link rel="stylesheet" href="{SW}/assets/app-menu.css?v=2">')
    print(f'<script src="{SW}/assets/app-menu.js?v=1" defer></script>')
    print(menu(cur, "/"))


def main():
    if "--site" in sys.argv:
        print_site(sys.argv[sys.argv.index("--site") + 1])
        return
    check = "--check" in sys.argv
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
            new = rewrite(text, current(rel), here)
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
