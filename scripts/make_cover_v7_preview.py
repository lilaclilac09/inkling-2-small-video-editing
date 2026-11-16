"""Build v7 cover preview — single photo (frame-0003, 0054-f03), normal font.

Cover choice (Aileen 2026-11-15 17:59-18:02, logged in requirements-log.md):
  frame-0003 (clip 0054) — woman with glasses centre-frame smiling
  (drink + tablet), green-trees girl beside her on the right.
  Cover font rule: NORMAL font, NO handwriting -> Montserrat.

Layout (canvas 1920x1080, cream #F7F1E5, adapted from make_cover_v7.py):
  - Photo frame-0003 (1280x720, 16:9): scaled proportionally, NO crop/stretch,
    warm/vivid grade (same grade() as v7 A/B/C). Centred: x=320, y=40.
  - Title block under the photo, left-aligned to the photo edge (x=320, y=780):
    "Cursor Cafe" / "Shanghai" (Montserrat 72) + bronze rule + "2026.07.19"
    (Montserrat 28, tracked). Same text as the v7 A/B/C covers.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

W, H = 1920, 1080
BG = (247, 241, 229)          # cream #F7F1E5
INK = (58, 44, 32)            # dark brown ink
TAUPE = (120, 100, 78)
BRONZE = (150, 125, 90)

PHOTO = "frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg"
OUT = "v7-cover-preview.jpg"


def grade(im):
    """Unified warm/vivid grade (korean-style), same as make_cover_v7.py."""
    im = im.convert("RGB")
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Brightness(im).enhance(1.05)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.04)))
    b = b.point(lambda v: int(v * 0.96))
    return Image.merge("RGB", (r, g, b))


def draw_tracked(d, xy, text, font, fill, tracking=6):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    canvas = Image.new("RGB", (W, H), BG)

    # Photo: original 1280x720 (16:9) -> fits the top zone (y=40..760) exactly
    # at 1280 wide; centred horizontally (x=320). No crop, no stretch.
    im = ImageOps.exif_transpose(Image.open(PHOTO))
    ow, oh = im.size
    assert (ow, oh) == (1280, 720), f"unexpected frame size {ow}x{oh}"
    im = grade(im)
    px, py = 320, 40
    canvas.paste(im, (px, py))
    print(f"  photo {PHOTO}: {ow}x{oh} pasted at ({px},{py})")

    # Title block, left-aligned to the photo edge.
    d = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype("fonts/Montserrat.ttf", 72)
    date_font = ImageFont.truetype("fonts/Montserrat.ttf", 28)
    tx, ty = px, 780
    d.text((tx, ty), "Cursor Cafe", font=title_font, fill=INK)
    lh = title_font.getbbox("Cursor Cafe")[3] + 12
    d.text((tx, ty + lh), "Shanghai", font=title_font, fill=INK)
    lh2 = title_font.getbbox("Shanghai")[3] + 12
    rule_y = ty + lh + lh2 + 18
    d.line([(tx + 4, rule_y), (tx + 336, rule_y)], fill=BRONZE, width=2)
    draw_tracked(d, (tx + 4, rule_y + 20), "2026.07.19", date_font, TAUPE, tracking=6)

    canvas.save(OUT, quality=92)
    print(f"Wrote {OUT} {canvas.size}")


if __name__ == "__main__":
    main()
