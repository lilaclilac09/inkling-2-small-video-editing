"""Build v7 cover preview v2 — 3-photo mood board with frame-0003 FEATURED.

Per Aileen 2026-11-15 22:04 (replying to the single-photo v7-cover-preview.jpg):
  (this one is good, put the other photos on there too; lay it out nicely).

Photos (full-frame, native aspect ratio, no crop/stretch, warm-graded):
  FEATURED  frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg (16:9) —
            two girls together: woman with glasses centre-frame smiling
            (drink + tablet), green-trees girl beside her on the right.
  OUTDOOR   photos/HM5A1893.JPG (3:2) — three girls at the storefront,
            peace sign at the Cursor banner.
  SPEAKER   frames-dense/DJI_20260719084815_0042_D/frame-0012.jpg (16:9) —
            Talk E woman presenting at the screen.

Layout (canvas 1920x1080, cream #F7F1E5, margin 40, gap 24) — same
structure as cover-v7 A/B/C, adjusted for the 16:9 featured photo:
  - frame-0003 (featured): x=40, y=40, w=1080, h=608 (16:9).
    Shorter than the old 3:2 featured (720), so the title block below
    it gets comfortable air instead of crowding.
  - HM5A1893 (outdoor):   x=1144, y=40, w=736, h=491.
  - 0042-f12 (speaker):   x=1144, y=555, w=736, h=414 (ends y=969).
  - Title block under the featured photo: x=40, y=680.
    "Cursor Cafe" / "Shanghai" (Montserrat 72pt, normal — NO handwriting)
    + bronze rule + "2026.07.19" (Montserrat 28pt, tracked).
  No cut-off heads, tones unified, text does not cover faces.

Output: v7-cover-preview-v2.jpg (does NOT overwrite v7-cover-preview.jpg,
the single-photo version she already approved).
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

W, H = 1920, 1080
BG = (247, 241, 229)          # cream #F7F1E5
INK = (58, 44, 32)            # dark brown ink
TAUPE = (120, 100, 78)
BRONZE = (150, 125, 90)

# (path, x, y, w) — height computed from the image's true aspect ratio
PANELS = [
    ("frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg", 40, 40, 1080),   # featured 16:9 -> h=608
    ("photos/HM5A1893.JPG", 1144, 40, 736),                                   # outdoor 3:2 -> h=491
    ("frames-dense/DJI_20260719084815_0042_D/frame-0012.jpg", 1144, 555, 736), # speaker 16:9 -> h=414
]


def grade(im):
    """Unified warm/vivid grade (korean-style), copied from make_cover_v7.py."""
    im = im.convert("RGB")
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Brightness(im).enhance(1.05)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.04)))
    b = b.point(lambda v: int(v * 0.96))
    return Image.merge("RGB", (r, g, b))


def build_panel(path, w):
    im = ImageOps.exif_transpose(Image.open(path))
    ow, oh = im.size
    aspect = ow / oh
    h = round(w / aspect)
    im = grade(im)
    panel = im.resize((w, h), Image.LANCZOS)
    print(f"  {path}: {ow}x{oh} aspect {aspect:.3f} -> panel {w}x{h}")
    return panel


def draw_tracked(d, xy, text, font, fill, tracking=6):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    canvas = Image.new("RGB", (W, H), BG)
    for path, x, y, w in PANELS:
        panel = build_panel(path, w)
        canvas.paste(panel, (x, y))
        print(f"  pasted {path} at ({x},{y}) {panel.size[0]}x{panel.size[1]}")
    d = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype("fonts/Montserrat.ttf", 72)
    date_font = ImageFont.truetype("fonts/Montserrat.ttf", 28)
    tx, ty = 40, 680
    d.text((tx, ty), "Cursor Cafe", font=title_font, fill=INK)
    lh = title_font.getbbox("Cursor Cafe")[3] + 12
    d.text((tx, ty + lh), "Shanghai", font=title_font, fill=INK)
    lh2 = title_font.getbbox("Shanghai")[3] + 12
    rule_y = ty + lh + lh2 + 18
    d.line([(tx + 4, rule_y), (tx + 336, rule_y)], fill=BRONZE, width=2)
    draw_tracked(d, (tx + 4, rule_y + 20), "2026.07.19", date_font, TAUPE, tracking=6)
    print(f"  title block: y {ty}..{rule_y + 20 + 28} (canvas bottom margin 1040)")
    canvas.save("v7-cover-preview-v2.jpg", quality=92)
    print(f"Wrote v7-cover-preview-v2.jpg {canvas.size}")


if __name__ == "__main__":
    main()
