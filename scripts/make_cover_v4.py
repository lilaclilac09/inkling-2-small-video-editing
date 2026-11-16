"""Build cover-v4.jpg — Somi-style 3-photo collage, 1920x1080.

Fixes vs cover-v3 (per Aileen 2026-11-13 15:31):
  - NO black bar: each panel is rendered 760px wide and composited
    over the previous one with a horizontal gradient alpha mask
    (0 -> 255 across a 120px seam band). The seam is pure
    photo-over-photo; there is no black underlay and no
    gradient-to-black anywhere in the image.
  - Lead photo is HM5A1822 (black-hat girl, front-facing, by the
    banner). HM5A1557 (hand across the frame) is NOT used.
  - Text is NOT Caveat. Playfair Display Bold (title) + Montserrat
    SemiBold (date), white with a soft shadow, bottom-centre over a
    subtle bottom gradient (bottom only — not a vertical seam).
  - Panels: (1) HM5A1822 black-hat girl, (2) HM5A1478 group by the
    Cursor banner, (3) DJI_20260719092002_0005_D indoor scene.

Usage: python3 make_cover_v4.py
Writes cover-v4.jpg in the current directory.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
PANEL_W = 640
BLEND = 120  # seam blend width in px
STRIP_W = PANEL_W + BLEND  # each panel rendered wider than its slot

# (source, crop-centre-x fraction after scaling to height H, x position)
PANELS = [
    ("photos/HM5A1822.JPG", 0.11, 0),       # black-hat girl (she stands at the left, ~11% across)
    ("photos/HM5A1478.JPG", 0.50, 580),     # group by banner
    ("photos/DJI_20260719092002_0005_D.JPG", 0.50, 1220),  # indoor scene
]


def strip(path, cx_frac):
    im = Image.open(path).convert("RGB")
    scale = H / im.height
    im = im.resize((round(im.width * scale), H), Image.LANCZOS)
    cx = int(im.width * cx_frac)
    x0 = max(0, min(im.width - STRIP_W, cx - STRIP_W // 2))
    return im.crop((x0, 0, x0 + STRIP_W, H))


def main():
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    for path, cx_frac, x in PANELS:
        s = strip(path, cx_frac)
        if x == 0:
            canvas.paste(s, (0, 0))
            continue
        # gradient alpha: 0 at the strip's left edge, 255 after BLEND px
        mask = Image.new("L", (STRIP_W, H), 0)
        md = ImageDraw.Draw(mask)
        for px in range(BLEND):
            md.line([(px, 0), (px, H)], fill=int(255 * px / (BLEND - 1)))
        md.rectangle([BLEND, 0, STRIP_W - 1, H - 1], fill=255)
        canvas.paste(s, (x, 0), mask)

    # Subtle bottom gradient for text legibility (bottom only).
    grad = Image.new("L", (W, 220), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(220):
        gd.line([(0, y), (W, y)], fill=int(150 * (y / 219) ** 1.6))
    black = Image.new("RGB", (W, 220), (0, 0, 0))
    canvas.paste(black, (0, H - 220), grad)

    d = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype("/tmp/fonts-v4/PlayfairDisplay-Bold.ttf", 76)
    date_font = ImageFont.truetype("/tmp/fonts-v4/Montserrat-SemiBold.ttf", 44)

    def text_center(y, text, font):
        bbox = d.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        d.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0))
        d.text((x, y), text, font=font, fill=(255, 255, 255))
        return tw

    text_center(902, "Cursor Cafe Shanghai", title_font)
    text_center(990, "2026.07.19", date_font)

    canvas.save("cover-v4.jpg", quality=92)
    print("Wrote cover-v4.jpg", canvas.size)


if __name__ == "__main__":
    main()
