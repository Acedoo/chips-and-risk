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


def make_card(path, headline, needle, houses, counts, date_txt, tagline):
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
    cx, cy, R = 960, 330, 165
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=PANEL, outline=RULE, width=3)
    d.line([cx - R, cy, cx + R, cy], fill=RULE, width=2)
    d.line([cx, cy - R, cx, cy + R], fill=RULE, width=2)
    pos = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    small, smallb = _font(False, 17), _font(True, 18)
    for k, h in houses.items():
        dx, dy = pos[h["point"]]
        px, py = cx + dx * R, cy + dy * R
        d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=COL[k])
        label = f"{h['name']} ({counts.get(k, 0)})"
        tw = d.textlength(label, font=smallb)
        tx = px - tw / 2
        ty = py - 40 if dy < 0 else py + 18
        tx = min(max(tx, 650), W - 20 - tw)
        d.text((tx, ty), label, font=smallb, fill=COL[k])
    if needle.get("mag", 0) > 0.05:
        nx, ny = cx + needle["x"] * R * 0.85, cy + needle["y"] * R * 0.85
        d.line([cx, cy, nx, ny], fill=INK, width=9)
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=INK)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=True)
