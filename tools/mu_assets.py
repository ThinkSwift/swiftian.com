#!/usr/bin/env python3
"""Mu page images from the app repo (art already live in the app or the store, so already reviewed).

- assets/mu/<mode>.webp : the phone screen cut out of the en-US iPhone store screenshot (no caption)
- assets/cards/<friend>_<nn>.webp : card art, the app's 720 px stickers at 360 px

Usage: python3 tools/mu_assets.py [path to MultiplicationTimesTables]
DEFEND (2.4) is added to SHOTS once 2.4 is live in App Store Connect.
"""
import os, sys
from PIL import Image

APP = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Projects/MultiplicationTimesTables")
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.path.join(APP, "fastlane/screenshots/en-US/iphone")
ART = os.path.join(APP, "MultiplicationTimesTables/ComicAssets/Characters/720px")

# store image -> (screen box). The phone sits lower under a two-line caption (learn).
SHOTS = {
    "learn": ("4_iphone_learn.png", (109, 580, 1096, 2622)),
    "race":  ("1_iphone_race.png",  (109, 453, 1096, 2577)),
    "hunt":  ("5_iphone_hunt.png",  (109, 453, 1096, 2577)),
}
# one card per rarity for each friend: common, rare (25-29), epic (30-31), legend (32)
CARDS = {"bear": [6, 25, 30, 32], "bunny": [7, 25, 30, 32], "cat": [5, 25, 30, 32],
         "frog": [10, 25, 30, 32], "red_panda": [6, 25, 30, 32]}

for name, (src, box) in SHOTS.items():
    im = Image.open(os.path.join(STORE, src)).convert("RGB").crop(box)
    im = im.resize((560, round(im.height * 560 / im.width)), Image.LANCZOS)
    out = os.path.join(SITE, "assets/mu", name + ".webp")
    im.save(out, "WEBP", quality=82, method=6)
    print(out, im.size, os.path.getsize(out))

n = 0
for friend, nums in CARDS.items():
    for num in nums:
        im = Image.open(os.path.join(ART, friend, f"{friend}_{num:02d}.png")).convert("RGBA")
        im = im.resize((360, 360), Image.LANCZOS)
        out = os.path.join(SITE, "assets/cards", f"{friend}_{num:02d}.webp")
        im.save(out, "WEBP", quality=88, method=6)
        n += 1
print(f"cards {n}/20")
