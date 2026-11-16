"""Build v7 cover combos v3/v4/v5 + comparison grid.

Per Aileen 2026-11-15 22:11 (replying to v7-cover-preview-v2.jpg):
  (find other options for the two on the right; try more combinations;
  let me see). Also the all-women composition is NOT a requirement;
  the right panels can feature anyone.

FEATURED stays frame-0003 (she liked it). Only the TWO RIGHT
panels change. Layout / grade / title reused from
make_cover_v7_preview_v2.py (featured left 1080 wide, two stacked
right 736 wide, title "Cursor Cafe" / "Shanghai" + bronze rule +
"2026.07.19" in Montserrat, cream #F7F1E5, warm grade, no
crop/stretch, no text over faces).

Combos (frame-0003 featured in all):
  v3: top HM5A1478 (big group photo) + bottom HM5A1923 (white-haired
      foreign man speaking at screen — she said his speech photo can
      also go in). Most different from v2: community + male speaker.
  v4: top HM5A1424 (7-person group, front row crouching smiling) +
      bottom 0042-f12 (Talk E woman presenting, kept from v2).
      Group up top, woman speaker below.
  v5: top HM5A1900 (two girls front-facing smiling at storefront) +
      bottom HM5A1789 (solo male speaker at screen, speaker=yes in
      photo-classification.jsonl — a different male speaker from the
      white-haired man). Different outdoor + different male speaker.

Layout note: right panels are w=736. A 3:2 bottom panel would be
h=491 and end at y=1046, 6px past the 40px bottom margin — so 3:2
bottom panels are clamped to h=485 (w=728) and centred in the slot.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

W, H = 1920, 1080
BG = (247, 241, 229)          # cream #F7F1E5
INK = (58, 44, 32)            # dark brown ink
TAUPE = (120, 100, 78)
BRONZE = (150, 125, 90)

FEATURED = "frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg"
SPEAKER_F12 = "frames-dense/DJI_20260719084815_0042_D/frame-0012.jpg"

COMBOS = {
    "v3": [("photos/HM5A1478.JPG", "top"),
           ("photos/HM5A1923.JPG", "bottom")],
    "v4": [("photos/HM5A1424.JPG", "top"),
           (SPEAKER_F12, "bottom")],
    "v5": [("photos/HM5A1900.JPG", "top"),
           ("photos/HM5A1789.JPG", "bottom")],
}

# Right-column slots: (x, y, w, max_h)
TOP_SLOT = (1144, 40, 736, 491)
BOTTOM_SLOT = (1144, 555, 736, 485)


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


def build_panel(path, w, max_h):
    """Scale proportionally to width w; if height exceeds max_h, scale
    down to fit max_h instead. Returns the panel image."""
    im = ImageOps.exif_transpose(Image.open(path))
    ow, oh = im.size
    aspect = ow / oh
    h = round(w / aspect)
    if h > max_h:
        h = max_h
        w = round(h * aspect)
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


def build_combo(name, right_panels):
    canvas = Image.new("RGB", (W, H), BG)
    # Featured frame-0003, left.
    feat = build_panel(FEATURED, 1080, 608)
    canvas.paste(feat, (40, 40))
    print(f"  pasted featured {FEATURED} at (40,40) {feat.size[0]}x{feat.size[1]}")
    # Right panels, centred in their slots if narrower than 736.
    for (path, slot_name) in right_panels:
        sx, sy, sw, sh = TOP_SLOT if slot_name == "top" else BOTTOM_SLOT
        panel = build_panel(path, sw, sh)
        px = sx + (sw - panel.size[0]) // 2
        canvas.paste(panel, (px, sy))
        print(f"  pasted {path} at ({px},{sy}) {panel.size[0]}x{panel.size[1]}")
    # Title block under the featured photo.
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
    out = f"v7-cover-{name}.jpg"
    canvas.save(out, quality=92)
    print(f"Wrote {out} {canvas.size}")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    for name, right_panels in COMBOS.items():
        print(f"== {name} ==")
        build_combo(name, right_panels)

    # ---- comparison image: 2x2 grid (v2, v3, v4, v5) ----
    names = [("v7-cover-preview-v2.jpg", "v2 — current (1893 + 0042-f12)"),
             ("v7-cover-v3.jpg", "v3 — group 1478 + white-haired man 1923"),
             ("v7-cover-v4.jpg", "v4 — group 1424 + speaker 0042-f12"),
             ("v7-cover-v5.jpg", "v5 — duo 1900 + male speaker 1789")]
    tw, th = 960, 540
    comp = Image.new("RGB", (tw * 2 + 30, th * 2 + 90), (255, 255, 255))
    dd = ImageDraw.Draw(comp)
    labelfont = ImageFont.truetype("fonts/Montserrat.ttf", 26)
    for i, (path, label) in enumerate(names):
        im = Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = (i % 2) * (tw + 30)
        y = (i // 2) * (th + 45)
        comp.paste(im, (x, y))
        dd.text((x + 8, y + th + 8), label, font=labelfont, fill=(30, 30, 30))
    comp.save("v7-cover-compare-v2v3v4v5.jpg", quality=92)
    print(f"Wrote v7-cover-compare-v2v3v4v5.jpg {comp.size}")


if __name__ == "__main__":
    main()
