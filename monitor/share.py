"""Weekly share card (1200x630 PNG) shown when the page is linked on LinkedIn, X or in a message:
brand, this week's sentence, the compass with its needle, and the date."""
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

INK, MUTED, RULE, PANEL = (20, 33, 61), (91, 107, 128), (227, 232, 239), (244, 247, 251)
COL = {"strong": (37, 99, 235), "weak": (224, 79, 79), "delay": (227, 162, 26), "fall": (20, 33, 61)}
FONT_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", "/Library/Fonts", "/System/Library/Fonts/Supplemental"]


def _font(bold, size):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for d in FONT_DIRS:
        p = Path(d) / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size=size)


def make_card(path, headline, needle, houses, counts, date_txt, tagline, labels=None):
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 10], fill=COL["strong"])
    d.text((60, 46), "Chips and Risk", font=_font(True, 40), fill=INK)
    d.text((60, 100), tagline, font=_font(False, 22), fill=MUTED)
    y = 170
    for line in textwrap.wrap(headline, width=37)[:8]:
        d.text((60, y), line, font=_font(False, 30), fill=INK)
        y += 44
    d.text((60, H - 70), date_txt, font=_font(False, 20), fill=MUTED)
    d.text((60, H - 42), "acedoo.github.io/chips-and-risk", font=_font(True, 20), fill=COL["strong"])
    cx, cy, R = 950, 330, 150
    lab = labels or {"listing": "Listing", "delay": "Delay", "fav": "Favourable", "adv": "Adverse"}
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=PANEL, outline=RULE, width=3)
    d.line([cx - R, cy, cx + R, cy], fill=MUTED, width=2)
    d.line([cx, cy - R, cx, cy + R], fill=MUTED, width=2)
    small, smallb = _font(False, 16), _font(True, 17)
    for t, (x, y, anchor) in ((lab["listing"], (cx - R + 6, cy + 8, "lt")), (lab["delay"], (cx + R - 6, cy + 8, "rt")),
                              (lab["fav"], (cx, cy - R - 12, "mb")), (lab["adv"], (cx, cy + R + 12, "mt"))):
        d.text((x, y), t, font=small, fill=MUTED, anchor=anchor)
    corners = {"strong": (-1, -1), "weak": (-1, 1), "delay": (1, -1), "fall": (1, 1)}
    mx = max(counts.values()) if counts and max(counts.values()) > 0 else 1
    for k, (dx, dy) in corners.items():
        n = counts.get(k, 0)
        dd = R * 0.7071
        if n:
            L = R * 0.9 * n / max(mx, 2) * 0.7071
            tip = (cx + dx * L, cy + dy * L)
            o = 22 * 0.7071
            light = tuple(int(255 - (255 - v) * 0.3) for v in COL[k])
            d.polygon([(cx - dy * o, cy + dx * o), tip, (cx + dy * o, cy - dx * o)], fill=light)
        px, py = cx + dx * dd, cy + dy * dd
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=COL[k])
        name = f"{houses[k]['name']} ({n})"
        tw = d.textlength(name, font=smallb)
        tx = px + 14 if dx > 0 else px - 14 - tw
        tx = min(max(tx, 640), W - 12 - tw)
        d.text((tx, py + (14 if dy > 0 else -32)), name, font=smallb, fill=COL[k])
    sc = max(1.0, (needle.get("x", 0) ** 2 + needle.get("y", 0) ** 2) ** 0.5)
    if needle.get("mag", 0) > 0.05:
        nx, ny = cx + needle["x"] / sc * R * 0.85, cy + needle["y"] / sc * R * 0.85
        d.line([cx, cy, nx, ny], fill=INK, width=8)
        d.text((nx + (10 if nx >= cx else -10), ny - 12), "OpenAI", font=smallb, fill=INK, anchor="ls" if nx >= cx else "rs")
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=INK)
    if needle.get("anthropic_x"):
        axp = cx + needle["anthropic_x"] * R * 0.85
        d.ellipse([axp - 9, cy - 9, axp + 9, cy + 9], fill="white", outline=(15, 157, 143), width=4)
        d.text((axp, cy - 16), "Anthropic", font=smallb, fill=(15, 157, 143), anchor="mb")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=True)
