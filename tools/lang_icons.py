#!/usr/bin/env python3
"""lang_icons.py — the language apps' pixel icons on the web (founder 2026-11-21, RDM-lang-icons-pixel-family).

One family: a white mark on one flat ground. EA = E on blue, CP = 中 on red (16x16 grids, 2-cell strokes),
SM = the founder's 말 on black (15x15 grid, 1-cell strokes; the cells are brand/SeoulMal-16.png's, only the
canvas changed). The grids below are copied from the roadmap row's 'spec' — change them there first.

Every size is the grid at a whole-number nearest-neighbour scale, centred on the ground; the margin absorbs
the difference, never the art (the SM tools/make_icons.py rule). Nothing is resampled smoothly.

    tools/lang_icons.py              # swiftian.com: the bar/menu icons every site loads
    tools/lang_icons.py --seoulmal   # also seoulmal.com: favicons, favicon.ico, touch icon, icon-app.png
                                     # (SM_SITE points at another checkout)
    tools/lang_icons.py --check      # exit 1 if a file differs from what the grids draw

Writes on swiftian.com: assets/tabs/ea-{32,64,96}.png, assets/tabs/cp-{32,64,96}.png,
assets/menu/sm-{32,64,96}.png. These used to come from different places (SM's make_icons.py --web wrote
sm-*); this tool is now the one source for them on the web.
"""
import io
import math
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SM_SITE = os.environ.get("SM_SITE", os.path.expanduser("~/Projects/seoulmal.com"))
WHITE = (255, 255, 255)

ICONS = {
    "EA": {"ground": (0x2C, 0x4F, 0x94), "grid": [
        "................", "................", "....########....", "....########....",
        "....##..........", "....##..........", "....##..........", "....########....",
        "....########....", "....##..........", "....##..........", "....##..........",
        "....########....", "....########....", "................", "................"]},
    "CP": {"ground": (0xC2, 0x1A, 0x13), "grid": [
        "................", "................", ".......##.......", ".......##.......",
        "...##########...", "...##########...", "...##..##..##...", "...##..##..##...",
        "...##########...", "...##########...", ".......##.......", ".......##.......",
        ".......##.......", ".......##.......", "................", "................"]},
    "SM": {"ground": (0, 0, 0), "grid": [
        "...............", "...............", "....#####.#....", "....#...#.#....",
        "....#...#.##...", "....#...#.#....", "....#####.#....", "...............",
        "....#######....", "..........#....", "....#######....", "....#..........",
        "....#######....", "...............", "..............."]},
}

SW_FILES = {"EA": "assets/tabs/ea-{}.png", "CP": "assets/tabs/cp-{}.png", "SM": "assets/menu/sm-{}.png"}
SW_SIZES = (32, 64, 96)
SM_FILES = {"favicon-16.png": 16, "favicon-32.png": 32, "favicon-48.png": 48,
            "apple-touch-icon.png": 180, "icon-app.png": 256}


def scale(px, n):
    """The whole-number scale nearest to px/n (a tie goes down), never larger than fits."""
    return max(1, min(px // n, math.ceil(px / n - 0.5)))


def draw(code, px):
    grid, ground = ICONS[code]["grid"], ICONS[code]["ground"]
    n = len(grid)
    assert all(len(r) == n for r in grid), code
    k = scale(px, n)
    art = Image.new("RGB", (n, n), ground)
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c == "#":
                art.putpixel((x, y), WHITE)
    big = art.resize((n * k, n * k), Image.NEAREST)
    out = Image.new("RGB", (px, px), ground)
    out.paste(big, ((px - n * k) // 2, (px - n * k) // 2))
    return out


def targets(seoulmal):
    for code, pattern in SW_FILES.items():
        for px in SW_SIZES:
            yield os.path.join(ROOT, pattern.format(px)), code, px
    if seoulmal:
        for name, px in SM_FILES.items():
            yield os.path.join(SM_SITE, name), "SM", px


def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def ico_bytes():
    buf = io.BytesIO()
    draw("SM", 48).save(buf, "ICO", sizes=[(16, 16), (32, 32), (48, 48)],
                        append_images=[draw("SM", 16), draw("SM", 32)])
    return buf.getvalue()


def same_pixels(path, img):
    try:
        old = Image.open(path).convert("RGB")
    except OSError:
        return False
    return old.size == img.size and old.tobytes() == img.tobytes()


def main():
    check = "--check" in sys.argv
    seoulmal = "--seoulmal" in sys.argv
    stale = []
    for path, code, px in targets(seoulmal):
        img = draw(code, px)
        if same_pixels(path, img):
            continue
        stale.append(os.path.relpath(path, os.path.dirname(ROOT)))
        if not check:
            with open(path, "wb") as f:
                f.write(png_bytes(img))
    if seoulmal:
        ico = os.path.join(SM_SITE, "favicon.ico")
        data = ico_bytes()
        try:
            current = open(ico, "rb").read()
        except OSError:
            current = b""
        if current != data:
            stale.append(os.path.relpath(ico, os.path.dirname(ROOT)))
            if not check:
                open(ico, "wb").write(data)
    total = sum(1 for _ in targets(seoulmal)) + (1 if seoulmal else 0)
    verb = "out of date" if check else "written"
    print(f"lang_icons: {len(stale)}/{total} {verb}")
    for p in stale:
        print("  " + p)
    return 1 if check and stale else 0


if __name__ == "__main__":
    sys.exit(main())
